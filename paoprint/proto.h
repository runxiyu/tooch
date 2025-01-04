// Received from the printer. We usually process them octet-by-octet so it's
// easier to define them as single characters here.

#define LPD_SUCCESS '\x00'

// Commands to send to the printer. We usually construct them into strings, so
// we declare them as string constatnts.

#define LPD_RECV_PRINTER_JOB "\x02"
#define LPD_RECV_DATA_FILE "\x03"

#define LPD_CFA "cfA"		// A control file associated with the proceeding job number, see §6.2.
#define LPD_DFA "dfA"		// A data file associated with the proceeding job number see §6.3.

#define LPD_CONTROL_HOST_NAME "H"
#define LPD_CONTROL_USER_IDENTIFICATION "P"
#define LPD_CONTROL_JOB_NAME_FOR_BANNER_PAGE "J"
#define LPD_CONTROL_NAME_OF_SOURCE_FILE "N"
#define LPD_CONTROL_PRINT_FILE_LEAVING_CONTROL_CHARACTERS "l"
#define LPD_CONTROL_UNLINK_DATA_FILE "U"

#define LPD_LF "\n"		// Commands are usually ended with a newline.
#define LPD_SP " "		// Some arguments are separated by spaces.
#define LPD_NUL "\0"		// Some arguments are separated by spaces.
