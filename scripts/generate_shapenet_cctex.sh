set -x
set -u
set -e

for i in {1..1000}
do
    echo "$i"
    CUDA_VISIBLE_DEVICES=0 python run.py \
    examples/shapenet_with_cctex/config.yaml \
    ~/datasets/render/shapenetcc2/ \
    ~/datasets/shapenet/ShapeNetCore.v2/ \
    /home/qiaog/datasets/cctextures_processed/ \
    ~/datasets/render/shapenetcc/ \
    resources/cctextures
done
