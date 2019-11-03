/*
 * Hidraw Userspace Example
 *
 * Copyright (c) 2010 Alan Ott <alan@signal11.us>
 * Copyright (c) 2010 Signal 11 Software
 *
 * The code may be used by anyone for any purpose,
 * and can serve as a starting point for developing
 * applications using hidraw.
 */
 
/* Linux */
#include <linux/types.h>
#include <linux/input.h>
#include <linux/hidraw.h>
#include <time.h>
 
/*
 * Ugly hack to work around failing compilation on systems that don't
 * yet populate new version of hidraw.h to userspace.
 *
 * If you need this, please have your distro update the kernel headers.
 */
#ifndef HIDIOCSFEATURE
#define HIDIOCSFEATURE(len)    _IOC(_IOC_WRITE|_IOC_READ, 'H', 0x06, len)
#define HIDIOCGFEATURE(len)    _IOC(_IOC_WRITE|_IOC_READ, 'H', 0x07, len)
#endif
 
/* Unix */
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
 
/* C */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
 
const char *bus_str(int bus);
 
int main(int argc, char **argv)
{
    time_t now;
    int fd;
    int i, res, desc_size = 0;
    char buf[256];
    struct hidraw_report_descriptor rpt_desc;
    struct hidraw_devinfo info;
    unsigned char epoch[4];
 
    fd = open("/dev/hidraw0", O_RDWR);
    if (fd < 0) {
        perror("Unable to open device /dev/hidraw0");
        fd = open("/dev/hidraw1", O_RDWR);
        if (fd < 0) {
            perror("Unable to open device /dev/hidraw1");
            return 1;
        }
    }
 
    memset(&rpt_desc, 0x0, sizeof(rpt_desc));
    memset(&info, 0x0, sizeof(info));
    memset(buf, 0x0, sizeof(buf));
 
    /* Set Feature */
    buf[0] = 0xb3; /* Report Number */
    buf[1] = 0x00;
    buf[2] = 0x00;
    buf[3] = 0x00;
    buf[4] = 0x00;
    buf[5] = 0x00;
    buf[6] = 0x00;
    buf[7] = 0x00;
     
    /* Send a Report to the Device */
    res = write(fd, buf, 8);
    if (res < 0) {
        printf("Error: %d\n", errno);
        perror("write");
    } else {
        //printf("write() wrote %d bytes\n", res);
    }
    
    /* Get a report from the device */
    res = read(fd, buf, 8);
    if (res < 0) {
        perror("read");
    } else {
        //printf("read() read %d bytes:\n\t", res);
        //for (i = 0; i < res; i++)
         //   printf("%hhx ", buf[i]);
        //puts("\n");
    }

    double noise = buf[0] * 256 + buf[1];
    noise = noise / 10;
    printf(" %f ", noise);
    close(fd);
    return 0;
}
 
const char *
bus_str(int bus)
{
    switch (bus) {
    case BUS_USB:
        return "USB";
        break;
    case BUS_HIL:
        return "HIL";
        break;
    case BUS_BLUETOOTH:
        return "Bluetooth";
        break;
    case BUS_VIRTUAL:
        return "Virtual";
        break;
    default:
        return "Other";
        break;
    }
}
