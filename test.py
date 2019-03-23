from collections import deque
deque = deque()
result = []
s = 'aabbaaabbc'

for i in s:
    if not deque:
        deque.append(i)
    elif i in deque:
        deque.append(i)
    else:
        data = ''
        while deque:
            data += deque.popleft()
        result.append(data)
        deque.append(i)
result.extend(deque)
print(' '.join(result))

