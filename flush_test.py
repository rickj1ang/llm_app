import time

print("Loading: ", end="")
for i in range(5):
    print(".", end="", flush=True)  # 可能等循环结束后才一起显示
    time.sleep(0.5)
