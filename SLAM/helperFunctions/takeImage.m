function im=takeImage(image_file_name_prefix,k)

    imRGB=imread(sprintf('%s%08d.png',image_file_name_prefix,k));
    
im=imRGB(:,:,:);