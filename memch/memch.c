/* 
 * Help memorize Chinese poetry/prose
 * SPDX-License-Identifier: BSD-2-Clause
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ncurses.h>
#include <time.h>
#include <signal.h>

#define NORMAL 1
#define WRONG 2
#define CORRECT 3
#define BLANK 4
#define HALF 5
#define ACTIVE 6

const char PUNCTS[] = "：；。！？，“”‘’"; // ascii quotes don't appear in Chinese text
// const char PUNCTS[] = ",."; // why would you ever use this

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
	char *text;
	bool display;
	char *ending_punctuation;
	int color;
};

void print_segments(struct segment *segments, int segment_count)
{
	int i;

	for (i = 0; i < segment_count; i++) {
		attron(COLOR_PAIR(segments[i].color));
		if (segments[i].display)
			printw("%s%s", segments[i].text, segments[i].ending_punctuation);
		else
			printw("*%s", segments[i].ending_punctuation);
		attroff(COLOR_PAIR(segments[i].color));
	}
}

struct segment *parse_paragraph_to_segments(const char *t, bool first_display, int *segment_count)
{
	int len = strlen(t);
	struct segment *segments;
	int i = 0, punct_idx = 0, text_idx = 0;
	bool current_display = first_display;
	char current_punctuation[10] = "";
	char current_text[1000] = "";

	if (len == 0)
		return NULL;

	segments = malloc(sizeof(*segments) * len);
	*segment_count = 0;

	while (true) {
		if (strchr(PUNCTS, t[i])) {
			current_punctuation[punct_idx++] = t[i++];
		} else if (punct_idx > 0) {
			current_punctuation[punct_idx] = '\0';
			segments[*segment_count].text = strdup(current_text);
			segments[*segment_count].display = current_display;
			segments[*segment_count].ending_punctuation = strdup(current_punctuation);
			segments[*segment_count].color = current_display ? NORMAL : BLANK;
			(*segment_count)++;
			current_punctuation[0] = '\0';
			punct_idx = 0;
			current_text[0] = '\0';
			text_idx = 0;
			current_display = !current_display;
		} else {
			current_text[text_idx++] = t[i++];
		}

		if (i >= len) { // FIXME
			current_text[text_idx] = '\0';
			segments[*segment_count].text = strdup(current_text);
			segments[*segment_count].display = current_display;
			segments[*segment_count].ending_punctuation = strdup(current_punctuation);
			segments[*segment_count].color = current_display ? NORMAL : BLANK;
			(*segment_count)++;
			break;
		}
	}

	return segments;
}

int main(int argc, char *argv[])
{
	signal(SIGINT, poof);

	FILE *file;
	struct segment *segments = NULL;
	char line[1000];
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

	while (fgets(line, sizeof(line), file)) {
		if (specified_line == -1 || current_line == specified_line) {
			line[strcspn(line, "\n")] = 0;
			if (strlen(line) > 0) {
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
		char got[1000];

		clear();
		print_segments(segments, segment_count);
		printw("\n\n");
		refresh();

		if (!segment->display) {
			mvprintw(LINES - 2, 0, "* ");
			echo();
			getnstr(got, sizeof(got) - 1);
			noecho();

			if (strcmp(got, segment->text) == 0) {
				segment->display = true;
				segment->color = CORRECT;
				corrects++;
			} else if (strlen(got) == 0) {
				segment->display = true;
				segment->color = WRONG;
				wrongs++;
			} else {
				mvprintw(LINES - 2, 0, "Retry: ");
				echo();
				getnstr(got, sizeof(got) - 1);
				noecho();

				if (strcmp(got, segment->text) == 0) {
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
