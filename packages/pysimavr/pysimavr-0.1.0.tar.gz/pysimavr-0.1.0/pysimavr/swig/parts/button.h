/*
 button.h

 This defines a sample for a very simple "peripheral"
 that can talk to an AVR core.
 It is in fact a bit more involved than strictly necessary,
 but is made to demonstrante a few useful features that are
 easy to use.

 Copyright 2008, 2009 Michel Pollet <buserror@gmail.com>

 This file is part of simavr.

 simavr is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 simavr is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with simavr.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef __BUTTON_H__
#define __BUTTON_H__

#include "sim_irq.h"

enum
{
	IRQ_BUTTON_OUT = 0, //
	IRQ_BUTTON_COUNT
};

typedef struct button_t
{
	avr_irq_t * irq; // output irq
	struct avr_t * avr;
	uint8_t value;
	int pullup; // 0=pulldown, 1=pullup
} button_t;

void button_init(struct avr_t * avr, button_t * b, const char * name, int pullup);
void button_press(button_t * b, uint32_t duration_usec);
void button_down(button_t * b);
void button_up(button_t * b);

#endif /* __BUTTON_H__*/
