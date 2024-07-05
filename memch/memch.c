/* 
 * Help memorize Chinese poetry/prose
 * Copyright (c) 2024 Runxi Yu <https://runxiyu.org>
 * SPDX-License-Identifier: BSD-2-Clause
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ncurses.h>
#include <time.h>
#include <signal.h>
#include <wchar.h>
#include <locale.h>

#define NORMAL 1
#define WRONG 2
#define CORRECT 3
#define BLANK 4
#define HALF 5
#define ACTIVE 6

const wchar_t PUNCTS[] = L"：；。！？，“”‘’"; // ascii quotes don't appear in Chinese text
// const wchar_t PUNCTS[] = L",."; // why would you ever use this

void poof(int sig)
{
	endwin();
	exit(0);
}

void warn(const char *progname, const char *s)
{
	fprintf(stderr, "%s: %s\n", progname, s);
}

struct segment {
	wchar_t *text;
	bool display;
	wchar_t *ending_punctuation;
	int color;
};

void print_segments(struct segment *segments, int segment_count)
{
	int i;

	for (i = 0; i < segment_count; i++) {
		attron(COLOR_PAIR(segments[i].color));
		if (segments[i].display)
			printw("%ls%ls", segments[i].text, segments[i].ending_punctuation);
		else
			printw("*%ls", segments[i].ending_punctuation);
		attroff(COLOR_PAIR(segments[i].color));
	}
}

struct segment *parse_paragraph_to_segments(const wchar_t *t, bool first_display, int *segment_count)
{
	int len = wcslen(t);
	struct segment *segments;
	int i = 0, punct_idx = 0, text_idx = 0;
	bool current_display = first_display;
	wchar_t current_punctuation[10] = L"";
	wchar_t current_text[1000] = L"";

	if (len == 0)
		return NULL;

	segments = malloc(sizeof(*segments) * len);
	*segment_count = 0;

	while (true) {
		if (wcschr(PUNCTS, t[i])) {
			current_punctuation[punct_idx++] = t[i++];
		} else if (punct_idx > 0) {
			current_punctuation[punct_idx] = L'\0';
			segments[*segment_count].text = wcsdup(current_text);
			segments[*segment_count].display = current_display;
			segments[*segment_count].ending_punctuation = wcsdup(current_punctuation);
			segments[*segment_count].color = current_display ? NORMAL : BLANK;
			(*segment_count)++;
			current_punctuation[0] = L'\0';
			punct_idx = 0;
			current_text[0] = L'\0';
			text_idx = 0;
			current_display = !current_display;
		} else {
			current_text[text_idx++] = t[i++];
		}

		if (i >= len) { // FIXME
			current_text[text_idx] = L'\0';
			segments[*segment_count].text = wcsdup(current_text);
			segments[*segment_count].display = current_display;
			segments[*segment_count].ending_punctuation = wcsdup(current_punctuation);
			segments[*segment_count].color = current_display ? NORMAL : BLANK;
			(*segment_count)++;
			break;
		}
	}

	return segments;
}

int main(int argc, char *argv[])
{
	setlocale(LC_ALL, "");

	signal(SIGINT, poof);

	FILE *file;
	struct segment *segments = NULL;
	wchar_t line[1000];
	int segment_count = 0;
	int specified_line = -1;
	int current_line = 0;
	int i, n;
	int wrongs = 0;
	int corrects = 0;

	if (argc < 2) {
		warn(argv[0], "Missing argument: Path to file to be memorized.");
		return 22;
	}

	file = fopen(argv[1], "r");
	if (!file) {
		warn(argv[0], "Cannot find file.");
		return 2;
	}

	if (argc > 2)
		specified_line = atoi(argv[2]) - 1;

	while (fgetws(line, sizeof(line) / sizeof(wchar_t), file)) {
		if (specified_line == -1 || current_line == specified_line) {
			line[wcscspn(line, L"\n")] = 0;
			if (wcslen(line) > 0) {
				struct segment *parsed_segments;
				int parsed_count;
				parsed_segments = parse_paragraph_to_segments(line, rand() % 2, &parsed_count);
				segments = realloc(segments, sizeof(struct segment) * (segment_count + parsed_count));
				for (i = 0; i < parsed_count; i++)
					segments[segment_count + i] = parsed_segments[i];
				segment_count += parsed_count;
				free(parsed_segments);
			}
		}
		current_line++;
		if (specified_line != -1 && current_line > specified_line)
			break;
	}

	fclose(file);

	if (segment_count == 0) {
		warn(argv[0], "Empty segments list after parsing.");
		return 79;
	}

	if (segments[0].display) {
		if (segment_count > 1)
			segments[1].color = ACTIVE;
	} else {
		segments[0].color = ACTIVE;
	}

	initscr();
	start_color();
	init_pair(NORMAL, COLOR_WHITE, COLOR_BLACK);
	init_pair(WRONG, COLOR_RED, COLOR_BLACK);
	init_pair(CORRECT, COLOR_GREEN, COLOR_BLACK);
	init_pair(BLANK, COLOR_YELLOW, COLOR_BLACK);
	init_pair(HALF, COLOR_MAGENTA, COLOR_BLACK);
	init_pair(ACTIVE, COLOR_CYAN, COLOR_BLACK);

	cbreak();
	noecho();
	keypad(stdscr, TRUE);

	for (i = 0; i < segment_count; i++) {
		struct segment *segment = &segments[i];
		wchar_t got[1000];

		clear();
		print_segments(segments, segment_count);
		printw("\n\n");
		refresh();

		if (!segment->display) {
			mvprintw(LINES - 2, 0, "* ");
			echo();
			getnstr((char*)got, sizeof(got) - 1);
			noecho();

			if (wcscmp(got, segment->text) == 0) {
				segment->display = true;
				segment->color = CORRECT;
				corrects++;
			} else if (wcslen(got) == 0) {
				segment->display = true;
				segment->color = WRONG;
				wrongs++;
			} else {
				mvprintw(LINES - 2, 0, "Retry: ");
				echo();
				getnstr((char*)got, sizeof(got) - 1);
				noecho();

				if (wcscmp(got, segment->text) == 0) {
					segment->display = true;
					segment->color = CORRECT;
					corrects++;
				} else {
					segment->display = true;
					segment->color = WRONG;
					wrongs++;
				}
			}

			n = i;
			while (n < segment_count && segments[n].display)
				n++;
			if (n < segment_count)
				segments[n].color = ACTIVE;
		}
	}

	clear();
	print_segments(segments, segment_count);
	printw("\n\n");
	printw("Summary:\nCorrect:    %d\nIncorrect:  %d\n", corrects, wrongs);
	refresh();

	getch();
	endwin();

	/*
	 * for (int i = 0; i < segment_count; i++) {
	 * 	free(segments[i].text);
	 * 	free(segments[i].ending_punctuation);
	 * }
	 * free(segments);
	 */
	// Let the OS handle the freeing instead, but uncomment when valgriding

	return 0;
}
