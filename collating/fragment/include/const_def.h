#ifndef __CONST_DEF_H__
#define __CONST_DEF_H__ 1

#if defined __linux__
#define PATH_MAGIC_DB "data/magic/media.mgc"
#elif defined _WIN32 || defined _WIN64
#define PATH_MAGIC_DB "data\\magic\\media.mgc"
#else
#error "Unsupported platform"
#endif

#endif /* __CONST_DEF_H__ */
