from pyvttbl import DataFrame
df = DataFrame()
df.read_tbl('example.csv')
print(df)

print df['X']
y = [23]*len(df['X'])
print y
print df.names()
df['X'] = y
print df.names()
print df

