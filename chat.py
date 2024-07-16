import os
from datetime import datetime
import time
from duckduckgo_search import AsyncDDGS
import asyncio
import concurrent.futures
from pprint import pp

dir_save = '/Users/macjianfeng/Dropbox/Downloads/'

async def fupdate(fpath, content=None):
    content = content or ""
    if os.path.exists(fpath):
        with open(fpath, 'r') as file:
            old_content = file.read()
    else:
        old_content = ''
        
    with open(fpath, 'w') as file:
        file.write(content)
        file.write(old_content)

async def echo_einmal(*args, **kwargs):
    """
    query, model="gpt", verbose=True, log=True, dir_save=dir_save
    """
    global dir_save
    
    query = None
    model = kwargs.get('model', 'gpt')
    verbose = kwargs.get('verbose', True)
    log = kwargs.get('log', True)
    dir_save = kwargs.get('dir_save', dir_save)
    
    for arg in args:
        if isinstance(arg, str):
            if os.path.isdir(arg):
                dir_save = arg
            elif len(arg) <= 5:
                model = arg
            else:
                query = arg
        elif isinstance(arg, dict):
            verbose = arg.get("verbose", verbose)
            log = arg.get("log", log)
    
    def is_in_any(str_candi_short, str_full, ignore_case=True):
        if isinstance(str_candi_short, str):
            str_candi_short = [str_candi_short]
        res_bool = []
        if ignore_case:
            [res_bool.append(i in str_full.lower()) for i in str_candi_short]
        else:
            [res_bool.append(i in str_full) for i in str_candi_short]
        return any(res_bool)

    def valid_mod_name(str_fly):
        if is_in_any(str_fly, "claude-3-haiku"):
            return "claude-3-haiku"
        elif is_in_any(str_fly, "gpt-3.5"):
            return "gpt-3.5"
        elif is_in_any(str_fly, "llama-3-70b"):
            return "llama-3-70b"
        elif is_in_any(str_fly, "mixtral-8x7b"):
            return "mixtral-8x7b"
        else:
            print(f"not support your model {model}, supported models: 'claude','gpt(default)', 'llama','mixtral'")
            return "gpt-3.5"  # default model

    model_valid = valid_mod_name(model)

    async def run_ddgs_chat(query, model_valid):
        async with AsyncDDGS() as ddgs:
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = await loop.run_in_executor(pool, ddgs.chat, query, model_valid)
        return res

    res = await run_ddgs_chat(query, model_valid)
    
    if verbose:
        print("\n") # add a newline
        pp(res)
        # print(res) 
    
    if log:
        dt_str = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')
        res_ = f"\n\n#### Q: {query}\n\n##### Ans: {dt_str}\n\n> {res}\n"
        if bool(os.path.basename(dir_save)):
            fpath = dir_save
        else:
            os.makedirs(dir_save, exist_ok=True)
            fpath = os.path.join(dir_save, "log_ai.md")
        await fupdate(fpath=fpath, content=res_)
        print(f"log file: {fpath}")
    
    return res

async def echo(*args, **kwargs):
    while True:
        try:
            print("\nEnter your query (or 'quit' to stop): ")
            query = input()
            if query.lower() == 'quit':
                break
            response = await echo_einmal(query, *args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            break
        await asyncio.sleep(0.5)
def chat(*args, **kwargs):
    return echo_einmal(*args, **kwargs)

def ai(*args, **kwargs):
    return echo_einmal(*args, **kwargs)

async def ai(*args, **kwargs):
    return echo_einmal(*args, **kwargs)

async def main():
    await echo(log=1)

if __name__ == "__main__":
    asyncio.run(main())