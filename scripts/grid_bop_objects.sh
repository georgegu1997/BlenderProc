set -x
set -u
set -e

# ycbv dataset
DATASET=ycbv
for i in {1..21}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# LM dataset
DATASET=lm
for i in {1..15}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# T-LESS dataset
DATASET=tless
for i in {1..30}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# tudl dataset
DATASET=tudl
for i in {1..3}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# tyol dataset
DATASET=tyol
for i in {1..21}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# ruapc dataset
DATASET=ruapc
for i in {1..14}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# icmi dataset
DATASET=icmi
for i in {1..6}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# icbin dataset
DATASET=icbin
for i in {1..2}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# itodd dataset
DATASET=itodd
for i in {1..28}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done

# hb dataset
DATASET=hb
for i in {1..33}
do
    python run.py examples/bop_object_grid/config.yaml examples/bop_object_grid/output/${DATASET}/$i/ ~/datasets/bop/ $DATASET $i
done
