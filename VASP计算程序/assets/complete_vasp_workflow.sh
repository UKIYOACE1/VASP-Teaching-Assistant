
#!/bin/bash


# 定义服务器的用户名和地址
SERVER_USER="xiaguangyu"
SERVER_ADDRESS="172.20.205.32"
SERVER_PATH="/home/xiaguangyu/0514/1"


# 定义相对于脚本的路径
LOCAL_PATH="./VASP_files"            #本地相对路径

# 文件列表，确保这些文件在你的本地路径中
UPLOAD_FILES="INCAR POSCAR KPOINTS POTCAR run.sh"
DOWNLOAD_FILES="CHG CONTCAR IBZKPT OSZICAR OUTCAR DOSCAR PROCAR CHGCAR EIGENVAL PCDAT REPORT WAVECAR XDATCAR vasprun.xml slurm-output.out"

# 使用scp命令上传文件
echo "开始上传文件..."
for file in $UPLOAD_FILES; do
    scp "$LOCAL_PATH/$file" "$SERVER_USER@$SERVER_ADDRESS:$SERVER_PATH/$file"
    if [ $? -eq 0 ]; then
        echo "文件 $file 上传成功"
    else
        echo "文件 $file 上传失败"
        exit 1  # 如果有任何一个文件上传失败，则终止脚本
    fi
done

# 登录到服务器并执行VASP计算
ssh $SERVER_USER@$SERVER_ADDRESS << 'EOF'
echo "已成功登录到服务器"


SERVER_PATH="/home/xiaguangyu/0514/1"


cd $SERVER_PATH
echo "当前工作目录：$(pwd)"

# 创建并提交VASP作业脚本


chmod +x run.sh
job_id=$(sbatch run.sh | awk '{print $4}')  # 提交作业并获取作业ID
echo "VASP计算任务已提交，作业ID为 $job_id。"

# 等待作业完成
echo "正在检测作业 $job_id 的完成状态..."
while squeue -j $job_id | grep -q "$job_id"
do
    echo "作业 $job_id 仍在运行中..."
    sleep 60  # 每60秒检查一次
done
echo "作业 $job_id 已完成。"
EOF

# 使用scp命令下载文件到本地并在成功后删除服务器上的文件
echo "开始下载文件..."
for file in $DOWNLOAD_FILES; do
    scp "$SERVER_USER@$SERVER_ADDRESS:$SERVER_PATH/$file" "$LOCAL_PATH/$file"
    if [ $? -eq 0 ]; then
        echo "文件 $file 下载成功"
        # 删除服务器上的文件
        ssh $SERVER_USER@$SERVER_ADDRESS "rm -f $SERVER_PATH/$file"
        if [ $? -eq 0 ]; then
            echo "已从服务器删除文件 $file"
        else
            echo "尝试删除服务器文件 $file 失败"
        fi
    else
        echo "文件 $file 下载失败"
    fi
done

# 删除服务器上的计算文件
echo "正在清理服务器上的计算文件..."
COMPUTE_FILES="INCAR POSCAR KPOINTS POTCAR run.sh"
for compute_file in $COMPUTE_FILES; do
    ssh $SERVER_USER@$SERVER_ADDRESS "rm -f $SERVER_PATH/$compute_file"
    if [ $? -eq 0 ]; then
        echo "已从服务器删除计算文件 $compute_file"
    else
        echo "尝试删除计算文件 $compute_file 失败"
    fi
done
