from nonebot.rule import to_me
import requests
from nonebot.plugin import on_command
from nonebot.adapters import Event,Message,MessageSegment,Bot
from nonebot.params import ArgPlainText
from nonebot.params import CommandArg
import shutil
import jmcomic, os, time, yaml
from PIL import Image
config = "./config.yml"
loadConfig = jmcomic.JmOption.from_file(config)
name=""
def all2PDF(input_folder, pdfpath, pdfname):
    start_time = time.time()
    paht = input_folder
    zimulu = []  # 子目录（里面为image）
    image = []  # 子目录图集
    sources = []  # pdf格式的图

    with os.scandir(paht) as entries:
        for entry in entries:
            if entry.is_dir():
                zimulu.append(int(entry.name))
    # 对数字进行排序
    zimulu.sort()

    for i in zimulu:
        with os.scandir(paht + "/" + str(i)) as entries:
            for entry in entries:
                if entry.is_dir():
                    print("这一级不应该有自录")
                if entry.is_file():
                    image.append(paht + "/" + str(i) + "/" + entry.name)

    if "jpg" in image[0]:
        output = Image.open(image[0])
        image.pop(0)

    for file in image:
        if "jpg" in file:
            img_file = Image.open(file)
            if img_file.mode == "RGB":
                img_file = img_file.convert("RGB")
            sources.append(img_file)

    pdf_file_path = pdfpath + "/" + pdfname
    if pdf_file_path.endswith(".pdf") == False:
        pdf_file_path = pdf_file_path + ".pdf"
    output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)
    end_time = time.time()
    run_time = end_time - start_time
    print("运行时间：%3.2f 秒" % run_time)
def jm_installer_to_pdf(jm_id):
    jmcomic.download_photo(jm_id,loadConfig,callback=to_pdf)
def to_pdf(ablum,d):
    global name,ab
    ab=ablum
    with open(config, "r",encoding="utf8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        path = data["dir_rule"]["base_dir"]


        all2PDF(path + "/" + ablum.name, path, ablum.name)
        name=path + "/" + ablum.name+".pdf"
    shutil.rmtree(path + "/" + ablum.name)
openj = on_command("jm", priority=10, block=True)

@openj.handle()
async def handle_function(bot:Bot, event: Event,args: Message = CommandArg()):
    await openj.send("正在下载")
    argjm=args.extract_plain_text()
    with open(config, "r",encoding="utf8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        path = data["dir_rule"]["base_dir"]
    try:
        jm_installer_to_pdf(argjm)
    except Exception as e:
        await openj.finish("出错了,似乎没有这个")
    
    authors="本篇作者:"+ab.author
    tags="本篇tag:"
    for i in ab.tags:
        tags=tags+i+","
    messge_id=await openj.send(authors+"\n"+tags)

    await openj.send("正在发送不好康的")
   #发送文件
    file=[
        {
	"type": "file",
    "data": {
        "file": "file://"+name,
        "name": argjm+".pdf"
    }}]
    messge_id=await bot.call_api("send_group_msg",group_id=event.group_id, message=file)
    await openj.finish("完成")
    
    