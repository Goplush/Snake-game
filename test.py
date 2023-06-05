def extract_substring(input_string):
    start_index = input_string.find('(') + 1  # 找到第一个左括号的索引并加1
    end_index = input_string.find(')')  # 找到第一个右括号的索引

    if start_index >= 0 and end_index >= 0 and end_index > start_index:
        substring = input_string[start_index:end_index]  # 提取子串
        return substring
    else:
        return None

# 示例用法
input_string = "这是一个(示例)字符串"
substring = extract_substring(input_string)
print(substring)