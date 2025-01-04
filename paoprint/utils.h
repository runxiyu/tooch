#include <sys/types.h>
ssize_t strmcat(char *dst, char *src, size_t dst_cap);
ssize_t strmcatx(char *dst, char *src, size_t dst_cap);
void sendc(int fd, char *buf, size_t n, int flags);
void sendx(int fd, char *content);
void sendbx(int fd, char content);
unsigned char recv_byte(int fd, char *buf);

