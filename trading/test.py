def process_data(data, callback):
    result = data * 2
    callback(result)

def print_result(result):
    print(f"结果是：{result}")

process_data(5, print_result)  # 输出：结果是：10