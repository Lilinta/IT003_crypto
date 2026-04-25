def find(g, p):
  for n in range(2, p):
    if pow(g, n, p) == g:
      return False
  return True

p = 28151
for g in range(p):
  if find(g, p):
    print(g)
    break
