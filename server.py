from re import T
import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import signal
import argparse
import uvicorn


start_logo = """
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║   ██╗  ██╗███████╗██╗     ██╗      ██████╗       ║
    ║   ██║  ██║██╔════╝██║     ██║     ██╔═══██╗      ║
    ║   ███████║█████╗  ██║     ██║     ██║   ██║      ║
    ║   ██╔══██║██╔══╝  ██║     ██║     ██║   ██║      ║
    ║   ██║  ██║███████╗███████╗███████╗╚██████╔╝      ║
    ║   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝ ╚═════╝       ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """
en_logo = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   ██████╗  ██████╗  ██████╗ ██████╗ ██████╗ ██╗   ██╗███████╗    ║
    ║  ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝    ║
    ║  ██║  ███╗██║   ██║██║   ██║██║  ██║██████╔╝ ╚████╔╝ █████╗      ║
    ║  ██║   ██║██║   ██║██║   ██║██║  ██║██╔══██╗  ╚██╔╝  ██╔══╝      ║
    ║  ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║   ███████╗    ║
    ║   ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚══════╝    ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """

# 在自动和手动结束时显示logo
def signal_hander(sig, frame):
    print(en_logo)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_hander)
signal.signal(signal.SIGTERM, signal_hander)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",type=str,default="127.0.0.1",help="host")# 监听地址
    parser.add_argument("--port",type=int,default=8000,help="port")       # 监听端口
    parser.add_argument("--reload",action="store_true",default=True,help="reload")     # 自动重载模块
    parser.add_argument("--log_level",type=str,default="info",choices=["debug", "info", "warning", "error", "critical"], help="Log level (default: info)")
    args = parser.parse_args()

    try:
        print(start_logo)# 打印开始logo
        uvicorn.run('src.main:app',host=args.host,port=args.port,reload=args.reload,log_level=args.log_level)
    
    except Exception as e:
        print(e)
        sys.exit(1)