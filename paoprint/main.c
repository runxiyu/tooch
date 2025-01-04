#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <err.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/sendfile.h>

#include "proto.h"
#include "config.h"
#include "utils.h"

int main(int argc, char **argv)
{
	if (argc != 2)
		errx(EXIT_FAILURE, "Provide exactly one argument, i.e. the filename to print");

	struct stat st;
	if (stat(argv[1], &st) != 0)
		err(EXIT_FAILURE, "stat: %s", argv[1]);
	__off_t file_size = st.st_size;
	int srcfd = open(argv[1], 0);
	if (srcfd < 0)
		err(EXIT_FAILURE, "open: %s", argv[1]);

	char rbuf[1];

	int sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0)
		err(EXIT_FAILURE, "socket");

	struct sockaddr_in server;
	server.sin_family = AF_INET;
	server.sin_port = htons(CONFIG_PORT);
	server.sin_addr.s_addr = inet_addr(CONFIG_HOST);
	if (connect(sockfd, (struct sockaddr *)&server, sizeof server) != 0)
		err(EXIT_FAILURE, "connect");
	// RFC1179 §3.1 says that the source part must be 721 to 731 inclusive,
	// but our school's implementation does not require that.

	// §5.2
	sendx(sockfd, LPD_RECV_PRINTER_JOB CONFIG_QUEUE LPD_LF);
	recv_byte(sockfd, rbuf);
	if (rbuf[0] != LPD_SUCCESS)
		errx(EXIT_FAILURE, "Job rejected while requesting initial queue");

	// Preparing §7
	char control_file[CONFIG_MAX_CONTROL_FILE_LENGTH] = "";
	size_t control_file_len;
	control_file_len = strmcatx(control_file, LPD_CONTROL_HOST_NAME CONFIG_HOSTNAME LPD_LF LPD_CONTROL_USER_IDENTIFICATION CONFIG_USER LPD_LF LPD_CONTROL_PRINT_FILE_LEAVING_CONTROL_CHARACTERS LPD_DFA CONFIG_JOB_NUMBER CONFIG_HOSTNAME LPD_LF LPD_CONTROL_JOB_NAME_FOR_BANNER_PAGE, CONFIG_MAX_CONTROL_FILE_LENGTH);
	control_file_len = strmcatx(control_file, argv[1], CONFIG_MAX_CONTROL_FILE_LENGTH);
	control_file_len = strmcatx(control_file, LPD_LF LPD_CONTROL_UNLINK_DATA_FILE LPD_DFA CONFIG_JOB_NUMBER CONFIG_HOSTNAME LPD_LF LPD_CONTROL_NAME_OF_SOURCE_FILE, CONFIG_MAX_CONTROL_FILE_LENGTH);
	control_file_len = strmcatx(control_file, argv[1], CONFIG_MAX_CONTROL_FILE_LENGTH);
	control_file_len = strmcatx(control_file, LPD_LF, CONFIG_MAX_CONTROL_FILE_LENGTH);

	// §6.2
	char control_file_header[CONFIG_MAX_CONTROL_FILE_HEADER_LENGTH] = "";
	size_t control_file_header_len;
	control_file_header_len = strmcatx(control_file_header, LPD_RECV_PRINTER_JOB, CONFIG_MAX_CONTROL_FILE_HEADER_LENGTH);
	control_file_header_len = snprintf(control_file_header + control_file_header_len, CONFIG_MAX_CONTROL_FILE_HEADER_LENGTH - control_file_header_len - 1, "%lu", control_file_len);
	control_file_header_len = strmcatx(control_file_header, LPD_SP LPD_CFA CONFIG_JOB_NUMBER CONFIG_HOSTNAME LPD_LF, CONFIG_MAX_CONTROL_FILE_HEADER_LENGTH);
	sendc(sockfd, control_file_header, control_file_header_len, 0);
	recv_byte(sockfd, rbuf);
	if (rbuf[0] != LPD_SUCCESS)
		errx(EXIT_FAILURE, "Job rejected while sending control file header");

	// Actually sending §7
	sendc(sockfd, control_file, control_file_len + 1, 0);
	recv_byte(sockfd, rbuf);
	if (rbuf[0] != LPD_SUCCESS)
		errx(EXIT_FAILURE, "Job rejected while sending control file");

	// §6.3
	char recv_data_file_line[CONFIG_MAX_RECV_DATA_FILE_LINE_LENGTH] = "";
	size_t recv_data_file_line_len;
	recv_data_file_line_len = strmcatx(recv_data_file_line, LPD_RECV_DATA_FILE, CONFIG_MAX_RECV_DATA_FILE_LINE_LENGTH);
	recv_data_file_line_len = snprintf(recv_data_file_line + recv_data_file_line_len, CONFIG_MAX_RECV_DATA_FILE_LINE_LENGTH - recv_data_file_line_len - 1, "%lu", file_size);
	recv_data_file_line_len = strmcatx(recv_data_file_line, LPD_SP LPD_DFA CONFIG_JOB_NUMBER CONFIG_HOSTNAME LPD_LF, CONFIG_MAX_RECV_DATA_FILE_LINE_LENGTH);
	sendx(sockfd, recv_data_file_line);
	recv_byte(sockfd, rbuf);
	if (rbuf[0] != LPD_SUCCESS)
		errx(EXIT_FAILURE, "Job rejected while sending data receive line");

	for (ssize_t sent = 0; sent < file_size;) {
		ssize_t res = sendfile(sockfd, srcfd, &sent, file_size - sent);
		if (res < 0) {
			err(EXIT_FAILURE, "sendfile");
		} else {
			sent += res;
		}
	}
	sendbx(sockfd, '\0');
	recv_byte(sockfd, rbuf);
	if (rbuf[0] != LPD_SUCCESS)
		errx(EXIT_FAILURE, "Job rejected while sending actual data");

	close(sockfd);
	close(srcfd);

	return EXIT_SUCCESS;
}
