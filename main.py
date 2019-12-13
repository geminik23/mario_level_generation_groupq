import sys
from groupq import GroupQLevelGenerator

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("it need config file to run : python3 main.py config.ini")
        sys.exit(1)

    generator = GroupQLevelGenerator(sys.argv[1])
    print("training time : {:.3f} secs".format(generator.train_levels()))
    generator.generate_levels()

    #print("generating time : {:.3f} secs".format(generator.generate_level()))
    #print("generated level is saved to {}".format( generator.save_file(0)))
