
CC = clang++
CFLAGS = -Wformat -g -fpermissive -std=c++14 -Wall
LDFLAGS = -lm


# from here on, no alterations should be necessary
#-------------------------------------------------

PROGRAM = abctab2ps

FONTS = fonts/frBaroqml.ps fonts/frFrancisque.ps \
	fonts/itBorrono.ps fonts/itTimes.ps \
	fonts/deCourier.ps fonts/deFraktur.ps

OBJECTS = abctab2ps.o oscompat.o parse.o syms.o style.o buffer.o \
	format.o pssubs.o subs.o util.o music.o tab.o


$(PROGRAM): $(OBJECTS)
	$(CC) -o $(PROGRAM) $(OBJECTS) $(LDFLAGS)


%.o: %.cpp %.h abctab2ps.h
	$(CC) $(CFLAGS) -c $*.cpp

tags: *.cpp *.h
	ctags  --defines --global -T --no-warn  *.cpp *.h

TAGS: *.cpp *.h
	etags *.cpp *.h

test:
	ABCTABFONTS=./fonts ./$(PROGRAM) -I sample.abc
	ABCTABFONTS=./fonts ./$(PROGRAM) sample.abc

clean:
	rm -f *.o Out.ps

purge:
	rm -f *.o $(PROGRAM) *.ps

