# Usage: sh generate_render_bop.sh <GPU_ID> <output_folder>
# Example usage: 
#   bash generate_render_bop.sh 0 /home/qiaog/datasets/render/shapenetccbop/

set -x
set -u
set -e

for i in {1..1000}
do
    echo "$i"
    CUDA_VISIBLE_DEVICES=$1 python run.py \
    examples/render_bop_objects/config.yaml \
    $2 \
    /home/qiaog/datasets/shapenet/ShapeNetCore.v2/ \
    /home/qiaog/datasets/cctextures_processed/ \
    $2 \
    resources/cctextures \
    /home/qiaog/datasets/bop
done