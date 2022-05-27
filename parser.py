import shutil
import pathlib


# copyfile(template, nfoName)
source_nfo = pathlib.Path('Runtime/template.nfo')
new_nfo = pathlib.Path('Runtime/new.nfo')

shutil.copyfile(source_nfo, new_nfo)

# pathlib
# new_nfo.write_text(new_nfo.read_text().replace('<SOURCE>', 'TESTING'))
# new_nfo.write_text(new_nfo.read_text().replace('<CHAPTERS>', 'TESTING AGAIN'))

# conetxt manager open()
# with open(source_nfo, 'r') as file:
    #     filedata = file.read()
    #     filedata = filedata.replace('<SOURCE>', 'TESTING')
    #     filedata = filedata.replace('<CHAPTERS>', 'TESTING AGAIN')
    # fileData = fileData.replace("<SOURCE>", sourceName)
    # fileData = fileData.replace("<CHAPTERS>", chapters)
    # fileData = fileData.replace("<SIZE>", size)
    # fileData = fileData.replace("<DURATION>", duration)
    # fileData = fileData.replace("<VIDEO_BIT_RATE>", str(videoBitRate))
    # fileData = fileData.replace("<RESOLUTION>", resolution)
    # fileData = fileData.replace("<ENCODER>", encoder)
    # fileData = fileData.replace("<SCREENS>", screenshots)
# with open(new_nfo, 'w') as file:
#     file.write(filedata)


