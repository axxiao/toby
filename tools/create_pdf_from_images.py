from os import listdir, rmdir, remove
from os.path import isfile, join
from fpdf import FPDF
import argparse
import re
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import traceback, sys


def is_image(filename):
    """
    Check if the file names shows it is an image
    :param filename: the file name
    :return: True - is .jpg/ .gif/ .png .jpeg
    """
    rtn = False
    try:
        file_ext = filename.rsplit('.', maxsplit=1)[1]
        if file_ext.lower() in ['jpg', 'gif', 'png', 'jpeg']:
            rtn = True
    except IndexError:
        pass
    return rtn


def create_pdf(parent_path, folder_name, output_path, h=297, overwrite=True,
               max_img_size=1024, output_error=False, delete_folder=True):
    """

    :param parent_path: absolute the base path
    :param folder_name: folder name to scan
    :param output_path: output path
    :param h: default to 297 the height of A4
    :param overwrite: default True,  when target files exist, if overwrite
    :param max_img_size: default to 1024,  max dimension of the image (if image is bigger than this, will shrik to this)
    :param output_error: default to False, option if output error
    :param delete_folder: default to True if delete the folder after PDF is created
    :return: N/A information is printed to stdout
    """
    created = False
    cur_path = join(parent_path, folder_name)
    # find file type: 
    image_list = [f for f in listdir(cur_path) if isfile(join(cur_path, f)) and is_image(f) and (f[0].isalpha() or f[0].isdigit())]
    pdf_name = folder_name + '.pdf'
    if not overwrite and isfile(join(output_path, pdf_name)):
        #should skip
        print(f'SKIP PDF {pdf_name} from {parent_path}' )
    elif len(image_list)>=10:        
        pdf = FPDF()
        pdf.set_auto_page_break(False, margin = 0.0)        
        print(f'Creating PDF {pdf_name} from {parent_path}' )
        try:
            err_cnt = 0
            for image in sorted(image_list, key=lambda x: int(re.findall(r'\d+', x)[0]) ):
                original_image = Image.open(join(cur_path, image))
                if original_image.size[1] >= original_image.size[0]:
                    # por        
                    rs_ratio = original_image.size[1]/max_img_size
                    ori = 'P'                    
                    hh = h
                else:
                    # horiz, recal                    
                    ori ='H'
                    a4 = 210/297 # default a4
                    rs_ratio = original_image.size[0]/max_img_size
                    r = original_image.size[0]/h
                    hh = h/297*210
                r = original_image.size[1]/hh # calculate ration
                w = int(original_image.size[0]/r)
                tgt=join(cur_path, 'resized_' + image)
                original_image=original_image.resize((int(original_image.size[0]/rs_ratio),
                                                      int(original_image.size[1]/rs_ratio)),Image.ANTIALIAS).convert("RGB")
                original_image.save(tgt,optimize=True,quality=95)
                try:
                    pdf.add_page(orientation=ori)
                    pdf.image(tgt, 0,0, w=w, h=hh)
                except:
                    err_cnt += 1
            if err_cnt <= len(image_list)/2:
                pdf.output(join(output_path, pdf_name), "F")
                print(f'Done  {pdf_name}', len(image_list), 'pages, missing', err_cnt)
                created = True
            else:
                print(f'Missing {pdf_name}', err_cnt, 'Pages!')
        except:
            if output_error:
                print(traceback.format_exception(*sys.exc_info()))
            print(f'!!ERROR  {pdf_name}', len(image_list), 'FAILED')
    else:
        print(f'No image found in {cur_path}' )
    for sub_folder_name in [d for d in listdir(cur_path) if not isfile(join(cur_path, d))]:
        create_pdf(cur_path, sub_folder_name, output_path, h=h,overwrite=overwrite,
                   max_img_size=max_img_size, output_error=output_error, delete_folder=delete_folder)
    if created and delete_folder and cur_path!=output_path:
        try:
            for f in [join(cur_path, f) for f in listdir(cur_path) if isfile(join(cur_path, f)) and '.pdf' not in f]:
                remove(f)
            rmdir(cur_path)
            print(f'\tCleaned up {cur_path}')
        except OSError as e:
            print("\tError Deleteing: %s : %s" % (cur_path, e.strerror))
    # end of create_pdf

def main(args):
    create_pdf(args.base, args.target, args.output, output_error=True,overwrite=False, delete_folder=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create PDF from images in folders')
    parser.add_argument('--base', type=str, required=True,
                        help = 'base working dir')
    parser.add_argument('--target', type=str, required=True,
                        help='target folder')
    parser.add_argument('--output', type=str, required=True,
                        help='output folder')
    main(parser.parse_args())
