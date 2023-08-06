import argparse
import Image


# parse our arguments
parser = argparse.ArgumentParser(description='Slice an image into rectangles sutable for tiled printing.')

parser.add_argument('filename')

parser.add_argument('-p', '--papersize', type=int, nargs=2, required=True, metavar=('width', 'height'), help='dimensions of a single tile sheet in inches')

parser.add_argument('-w', '--wallsize', type=int, nargs=2, required=True, metavar=('width', 'height'), help='total dimensions of the wall in feet')

parser.add_argument('-v', '--verbose', action='count', help='print debug information')

args = parser.parse_args()

# source image
try:
    source_image = Image.open(str(args.filename))
    if args.verbose > 0:
        print source_image.format, source_image.size, source_image.mode
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
    quit()

# paper size in inches
paper_size = args.papersize

# wall size in feet
wall_size = args.wallsize

# first, determine the number of sheets required:
number_of_sheets = ((wall_size[0] * 12) / paper_size[0], (wall_size[1] * 12) / paper_size[1])
if args.verbose > 0:
    print "Sheets X: " + str(number_of_sheets[0])
    print "Sheets Y: " + str(number_of_sheets[1])
    print "Total: " + str(number_of_sheets[0] * number_of_sheets[1])

# next, determine the dimension of each sheet in pixels:
slice_size = (source_image.size[0] / number_of_sheets[0], source_image.size[1] / number_of_sheets[1])

# for good measure, compare aspect ratio of sheet size and image slices:
if args.verbose > 0:
    print "Sheet aspect ratio: " + str(float(paper_size[0]) / float(paper_size[1]))
    print "Slice aspect ratio: " + str(float(slice_size[0]) / float(slice_size[1]))

current_row = 0
current_column = 0

# let's start slicing!
# we're going to work column by column
print "Slicing..."
for x in range(0, number_of_sheets[0]):
    for y in range (0, number_of_sheets[1]):
        box = (x * slice_size[0], y * slice_size[1], (x + 1) * slice_size[0], (y + 1) * slice_size[1])


        
        slice = source_image.crop(box)
        out = Image.new('RGBA', slice_size, (0, 0, 0, 0))
        out.paste(slice, (0, 0, slice_size[0], slice_size[1]))
        outfile = str(x) + "-" + str(y) + ".tif"
        
        # print useful debugging information if requested
        if args.verbose > 1:
            print outfile
            print box
        
        out.save(outfile)

print "Done!"