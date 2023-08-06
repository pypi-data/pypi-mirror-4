# Makefile for nfftls (tailored for GNU make).
#
# \author B. Leroy
#
# This file is part of nfftls.
#
# Nfftls is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Nfftls is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with nfftls.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012 by B. Leroy
#

# 
# make               builds program nfftls
# make BENCHMARK=on  builds program nfftls with measurement of
#                    running time of periodogram computation
# make clean         remove object files and development library
# make cleanall      remove exectuable, object files
#
PROG = nfftls

LIBDEVEL = libdevel.a

RM = rm -f
CC = gcc

ifeq ($(BENCHMARK), on)
  XCFLAGS=-DBENCHMARK
else
  XCFLAGS=
endif

CFLAGS = -Wall -O2  -g $(XCFLAGS) -I /usr/local/include/   -finline-functions -I/usr/include/python2.6  -std=c99  -malign-double   -fPIC 

LDLIBS = -L.  -lnfft3 -lfftw3 -lm -lc 

SRCS = io.c \
       ls.c \
       nfft.c \
       usage.c \
       utils.c \
	pynfftls.c	

OBJS = $(SRCS:.c=.o)

HEADERS = io.h \
          ls.h \
          nfft.h \
          usage.h \
          utils.h

DEPEND = $(SRCS:.c=.d)

ARCHIVE-FILES = $(SRCS) $(HEADERS) $(PROG:=.c) Makefile \
                COPYING README

$(PROG) : $(LIBDEVEL)

$(LIBDEVEL) : $(OBJS)
	ar rsuv $@ $?


archive: $(ARCHIVE-FILES)
	@echo $(PROG)-`perl -ne \
         '/const char\* VersionStr = \"(.+)\";/ && print "$$1\n"' nfftls.c` > .fname
	@-rm -fr `cat .fname`
	@mkdir `cat .fname`
	@ln $(ARCHIVE-FILES) `cat .fname`
	@tar chzf `cat .fname`.tgz `cat .fname`
	@echo Created archive `cat .fname`.tgz
	@-rm -fr `cat .fname` .fname

python:  $(SRC)
	python setup.py build

python-install: python
	python setup.py install --home $(HOME)

clean:
	$(RM) $(OBJS) $(LIBDEVEL) $(DEPEND) files-to-archive
	$(RM) -r build/

cleanall: clean
	$(RM) $(PROG)

$(OBJS) : $(HEADERS)

# Include dependencies only if target is not
# clean*, archive, or if make has been
# invoked without any target.
ifneq "$(findstring clean, $(MAKECMDGOALS))" "clean"
  include $(DEPEND)
endif

# Defines object suffix for profiling
# and automatic dependencies generation
.SUFFIXES: .d

# For automatic dependencies generation
%.d: %.c
	$(CC) -MM $(CPPFLAGS) $< > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	$(RM) $@.$$$$
