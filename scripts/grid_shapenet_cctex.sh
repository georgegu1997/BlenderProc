set -x
set -u
set -e

for i in {1..200}
do
    echo "$i"
    CUDA_VISIBLE_DEVICES=1 python run.py \
    examples/shapenet_with_cctex_grid/config.yaml \
    examples/shapenet_with_cctex_grid/output/$i/ \
    ~/datasets/shapenet/ShapeNetCore.v2/ \
    /home/qiaog/datasets/cctextures_processed/ \
    $i
done
