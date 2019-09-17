cd output

tftp $1 <<'EOF'
binary
put u-boot-restore.img
put u-boot-spl-restore.bin
put am335x-boneblack.dtb
put zImage
quit
EOF
