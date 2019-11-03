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
 
    /* Open the Device with non-blocking reads. In real life,
       don't use a hard coded path; use libudev instead. */
    //fd = open("/dev/hidraw1", O_RDWR|O_NONBLOCK);
    fd = open("/dev/hidraw0", O_RDWR);
 
    if (fd < 0) {
        perror("Unable to open device");
        return 1;
    }
 
    memset(&rpt_desc, 0x0, sizeof(rpt_desc));
    memset(&info, 0x0, sizeof(info));
    memset(buf, 0x0, sizeof(buf));
 
    /* Get Report Descriptor Size */
    /*
    res = ioctl(fd, HIDIOCGRDESCSIZE, &desc_size);
    if (res < 0)
        perror("HIDIOCGRDESCSIZE");
    else
        printf("Report Descriptor Size: %d\n", desc_size);
    */ 
    /* Get Report Descriptor */
    /*
    rpt_desc.size = desc_size;
    res = ioctl(fd, HIDIOCGRDESC, &rpt_desc);
    if (res < 0) {
        perror("HIDIOCGRDESC");
    } else {
        printf("Report Descriptor:\n");
        for (i = 0; i < rpt_desc.size; i++)
            printf("%hhx ", rpt_desc.value[i]);
        puts("\n");
    }
    */ 
 
    /* Get Raw Name */
    /*
    res = ioctl(fd, HIDIOCGRAWNAME(256), buf);
    if (res < 0)
        perror("HIDIOCGRAWNAME");
    else
        printf("Raw Name: %s\n", buf);
    */ 
 
    /* Get Physical Location */
    /*
    res = ioctl(fd, HIDIOCGRAWPHYS(256), buf);
    if (res < 0)
        perror("HIDIOCGRAWPHYS");
    else
        printf("Raw Phys: %s\n", buf);
    */ 
 
    /* Get Raw Info */
    /*
    res = ioctl(fd, HIDIOCGRAWINFO, &info);
    if (res < 0) {
        perror("HIDIOCGRAWINFO");
    } else {
        printf("Raw Info:\n");
        printf("\tbustype: %d (%s)\n",
            info.bustype, bus_str(info.bustype));
        printf("\tvendor: 0x%04hx\n", info.vendor);
        printf("\tproduct: 0x%04hx\n", info.product);
    }
    */ 
 
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

/*
    time(&now);
    char* c_time_string = ctime(&now);
    struct tm * p = localtime(&now);
    char s[1000];
    strftime(s, 1000, "%d-%m-%Y %H:%M:%S", p);
    printf("%s, ", s);
    //printf("Today is : %s", ctime(&now));
*/
    double noise = buf[0] * 256 + buf[1];
    noise = noise / 10;
    //printf("noise = %f\n", noise);
    //printf("gm1356 = %f , ", noise);
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
