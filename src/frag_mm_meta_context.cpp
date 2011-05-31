// HowToUse - Example for MediaInfoLib (commandline version)
// Copyright (C) 2004-2008 Jerome Martinez, Zen@MediaArea.net
//
// This library is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
//
//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//
// Example for MediaInfoLib
// Command line version
//
//+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#ifdef MEDIAINFO_LIBRARY
    #include "MediaInfo/MediaInfo.h" //Staticly-loaded library (.lib or .a or .so)
    #define MediaInfoNameSpace MediaInfoLib;
#else //MEDIAINFO_LIBRARY
    #include "MediaInfoDLL/MediaInfoDLL.h" //Dynamicly-loaded library (.dll or .so)
    #define MediaInfoNameSpace MediaInfoDLL;
#endif //MEDIAINFO_LIBRARY
#include <iostream>
#include <iomanip>
#include <sstream>
using namespace MediaInfoNameSpace;

#ifdef __MINGW32__
    #ifdef _UNICODE
        #define _itot _itow
    #else //_UNICODE
        #define _itot itoa
    #endif //_UNICODE
#endif //__MINGW32

//***************************************************************************
// By buffer example
//***************************************************************************
//---------------------------------------------------------------------------
//Note: you can replace file operations by your own buffer management class
#include <stdio.h>
int main (int argc, Char *argv[])
{
    std::stringstream lStringStream (std::stringstream::in | std::stringstream::out);
    int long lOffset = 0;
    int long lNumBytes = 0;
    int long lNumBytesRead = 0;

    if (argc != 4)
    {
        std::cerr << "Usage: " << argv[0] << " filename offset readbytes" << std::endl;
        return -1;
    }

    lStringStream << argv[2];
    lStringStream >> lOffset;
    lStringStream.clear();
    lStringStream << argv[3];
    lStringStream >> lNumBytes;

    //From: preparing an example file for reading
    FILE* F=fopen(argv[1], "rb"); //You can use something else than a file
    if (F==0)
        return 1;

    //From: preparing a memory buffer for reading
    unsigned char* From_Buffer=new unsigned char[512]; //Note: you can do your own buffer
    size_t From_Buffer_Size; //The size of the read file buffer

    //From: retrieving file size
    fseek(F, 0, SEEK_END);
    long F_Size=ftell(F);
    fseek(F, 0, SEEK_SET);

    // apply offset
    fseek(F, lOffset, SEEK_SET);

    //Initializing MediaInfo
    MediaInfo MI;

    //Preparing to fill MediaInfo with a buffer
    MI.Open_Buffer_Init(F_Size, 0);

    //The parsing loop
    do
    {
        if (lNumBytesRead >= lNumBytes)
        {
            break;
        }
        //Reading data somewhere, do what you want for this.
        From_Buffer_Size=fread(From_Buffer, 1, 512, F);
        lNumBytesRead += From_Buffer_Size;

        //Sending the buffer to MediaInfo
        size_t Status=MI.Open_Buffer_Continue(From_Buffer, From_Buffer_Size);
        if (Status&0x08) //Bit3=Finished
            break;

        //Testing if there is a MediaInfo request to go elsewhere
#if 0
        if (MI.Open_Buffer_Continue_GoTo_Get()!=(MediaInfo_int64u)-1)
        {
            fseek(F, (long)MI.Open_Buffer_Continue_GoTo_Get(), SEEK_SET);   //Position the file
            MI.Open_Buffer_Init(F_Size, ftell(F));                          //Informing MediaInfo we have seek
        }
#endif
    }
    while (From_Buffer_Size>0);

    //Finalizing
    MI.Open_Buffer_Finalize(); //This is the end of the stream, MediaInfo must finnish some work

    //Get() example
    //String To_Display=MI.Get(Stream_Video, 0, _T("Width"));
    //String To_Display=MI.Inform_Get()

    #ifdef _UNICODE
        std::wcout << To_Display;
    #else
        std::cout << "Codec: " << MI.Get(Stream_Video, 0, _T("Codec")) << std::endl;
        std::cout << "Width: " << MI.Get(Stream_Video, 0, _T("Width")) << std::endl;
        std::cout << "Height: " << MI.Get(Stream_Video, 0, _T("Height")) << std::endl;
    #endif

    delete [] From_Buffer;
}

