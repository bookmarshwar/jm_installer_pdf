from nonebot.rule import to_me
import requests
from nonebot.plugin import on_command
from nonebot.adapters import Event,Message,MessageSegment,Bot
from lib.checkQQt import check_permission_as
from nonebot.params import ArgPlainText
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.exception import NetworkError
import shutil
import jmcomic, os, time, yaml
from jmcomic.jm_exception import MissingAlbumPhotoException
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
    try :
        jmcd=jmcomic.JmDownloader(loadConfig)
        c=loadConfig.build_jm_client()
        a=c.get_album_detail(argjm)
    except Exception as e:
        await openj.finish("出错了,似乎没有这个")
    from pathlib import Path

    folder = Path(path)
    pdf_o=[
        {
	"type": "file",
    "data": {
        "file": "file://"+path + "/" + a.name+".pdf",
        "name": argjm+".pdf"
    }}]
    for file in folder.glob('*'):
        if file.is_file():  # 虽然你说没有文件夹，但保留检查更安全
            if file.name==a.name+".pdf":
                await openj.send("已经存在,正在发送不好康的")
                try:
                    await bot.call_api("send_group_msg",group_id=event.group_id, message=pdf_o)
                except NetworkError as e:
                    await openj.finish(f"发送失败,{e.msg}")
                await openj.finish("完成")
    try:
        jm_installer_to_pdf(argjm)
    except Exception as e:
        await openj.finish("出错了,似乎没有这个")
    authors="本篇作者:"+a.author
    tags="本篇tag:"
    for i in a.tags:
        tags=tags+i+","
    messge_id=await openj.send(authors+"\n"+tags)
    """ 
    requests.post(url='http://127.0.0.1:9999/revoke',json={
    "id":f"{messge_id['message_id']}",
    "time":30
 })"""
    await openj.send("正在发送不好康的")
    try:
     messge_id=await bot.call_api("send_group_msg",group_id=event.group_id, message=pdf_o)
    except NetworkError as e:
        await openj.finish(f"发送失败,{e.msg}")
    await openj.finish("完成")
    """
    m1=[
        {
            "type": "reply",
            "data": {
                "id": messge_id["message_id"]
            }
        },
        {
            "type": "text",
            "data": {
                "text": "注意身体"
            }
        }
    ]
    messge_id=await bot.call_api("send_private_msg",user_id=bot.self_id, message=m1)
    m2 = [
        {
		"type": "node",
		"data": {
                            "nickname": "丁勇",
                "user_id": 10,
			"id":messge_id["message_id"],
		}
	}]
    messge_id=await bot.call_api("send_private_forward_msg",user_id=bot.self_id, message=m2)
    m2 = [
        {
		"type": "node",
		"data": {
                "nickname": "丁勇",
                "user_id": 10,
			"content":[
                {
            "type": "reply",
            "data": {
                "content":[
                     {
	"type": "file",
    "data": {
        "file": name,
        "name": argjm+".pdf"
    }}
                ]
            }
        },
        {
            "type": "text",
            "data": {
                "text": "注意身体"
            }
        }
            ]
		}
	}]
    await bot.call_api("send_group_forward_msg",group_id=event.group_id, messages=m2)
    await openj.finish("ok")

    """
    """
    print(messge_id)
    me=[
        {

            "type": "reply",
            "data": {
                "id": messge_id
            }
        },
        {
            "type": "text",
            "data": {
                "text": "注意身体"
            }
        }
    ]

    messge_id=await bot.call_api("send_private_msg",user_id=bot.self_id, message=file)
    rely = [
        {
		"type": "node",
		"data": {
			"id":messge_id["message_id"],
		}
	}]
    reply2=[
        {
            "type": "node",
            "data": {
                "content": [

                    {
                        "type": "reply",
                        "data": {
                            "id": messge_id["message_id"]
                        }
                    },
                    {
                        "type": "text",
                        "data": {
                            "text": "注意身体"
                        }
                    }
                ]
            }
        }
    ]
    messge_id=await bot.call_api("send_private_forward_msg",user_id=bot.self_id, messages=rely)
    rely = [
        {
		"type": "node",
		"data": {
			"id":messge_id["message_id"],
		}
	}]
    await bot.call_api("send_group_forward_msg",group_id=event.group_id, messages=rely)

    await openj.finish("ok")
    
    """
    