def zh(time):
    if '-' in time:
        splitter='-'
    elif ':' in time:
        splitter=':'
    else:
        return(time)
    (mine,secs)=time.split(splitter)
    return(mine+'.'+secs)

    
