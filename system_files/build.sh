STAGE=intermediate
FS=initramfs
OUT=output
mkdir -p $STAGE 
cd $FS

echo "Building Initramfs"
find . | cpio -H newc -o > ../$STAGE/$FS.cpio
cd .. && cat $STAGE/$FS.cpio | gzip > $STAGE/ramdisk.cpio.gz

cd $STAGE
cp ../maker/maker.its .
cp ../maker/kernel zImage 
cp ../maker/bbb_device_tree.dtb am335x-boneblack.dtb
mkimage -f maker.its fit
cd ..

mkdir -p $OUT
cp $STAGE/fit $OUT/zImage
cp bin/u-boot-restore.img $OUT/
cp bin/u-boot-spl-restore.bin $OUT/
cp bin/am335x-boneblack.dtb $OUT/
