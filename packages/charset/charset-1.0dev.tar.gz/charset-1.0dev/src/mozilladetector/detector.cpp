#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "detector.h"


CharSetDetector::CharSetDetector(PRUint32 aLanguageFilter) : nsUniversalDetector(aLanguageFilter){
    _detected_charset = NULL;
}

CharSetDetector::~CharSetDetector(){
    if (_detected_charset != NULL)
        free(_detected_charset);
}

char *CharSetDetector::DetectedCharset(){
    if (_detected_charset == NULL)
        return NULL;
    char *result = (char*)malloc(strlen(_detected_charset)+1);
    strcpy(result, _detected_charset);
    result[strlen(_detected_charset)] = 0;
    return result;
}

void CharSetDetector::Report(const char* aCharset){
    if (_detected_charset != NULL)
        free(_detected_charset);
    _detected_charset = (char*)malloc(strlen(aCharset)+1);
    strcpy(_detected_charset, aCharset);
    _detected_charset[strlen(aCharset)] = 0;
}


CharSetDetectorContext *charset_detector_create(PRUint32 aLanguageFilter){
    CharSetDetectorContext *result = (CharSetDetectorContext*)malloc(sizeof(CharSetDetectorContext));
    result->obj = (void *)new CharSetDetector(aLanguageFilter);
    return result;
}
void charset_detector_fee(CharSetDetectorContext * detector){
    if (detector != NULL){
        if (detector->obj != NULL)
            delete (CharSetDetector *)detector->obj;
        free(detector);
    }
}
void charset_detector_handle_data(CharSetDetectorContext * detector, const char *buff, int length){
    if (detector != NULL && detector->obj != NULL){
        ((CharSetDetector *)(detector->obj))->HandleData(buff, length);
    }
}
void charset_detector_data_end(CharSetDetectorContext * detector){
    if (detector != NULL && detector->obj != NULL){
        ((CharSetDetector *)(detector->obj))->DataEnd();
    }
}
char *charset_detector_detected_charset(CharSetDetectorContext * detector){
    if (detector != NULL && detector->obj != NULL){
        return ((CharSetDetector *)(detector->obj))->DetectedCharset();
    }
    return NULL;
}



char* charset_detect(const char *buff, int length){
    CharSetDetector detector(NS_FILTER_ALL);
    detector.HandleData(buff, length);
    detector.DataEnd();
    char *result = detector.DetectedCharset();
    if (result == NULL){
        result = (char*)malloc(6);
        strcpy(result, "ascii");
        result[5] = 0;
    }
    return result;
}
