from multiprocessing import Process

def f(name):
    print ('hello', name)

if __name__ == '__main__':
    q=['moe ', 'larry ', 'moe ', 'curly ', 'shemp ']
    for number in range(len(q)):
        print(number)
    for index in range(len(q)):
        p = Process(target=f, args=(q(index),))
        p.start()
        p.join()
