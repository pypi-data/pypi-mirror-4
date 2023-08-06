
#include <stdio.h>
#include <stddef.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>   /* XXX for ssize_t on some platforms */

#ifdef _WIN32
#  include <Windows.h>
#  define snprintf _snprintf
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef SSIZE_T ssize_t;
#else
#  include <stdint.h>
#endif


#include <postgres_ext.h>
#include <libpq-fe.h>
        
int _cffi_f_PQserverVersion(PGconn const *  x0)
{
  return PQserverVersion(x0);
}

int _cffi_e__PGTransactionStatusType(char *out_error)
{
  if (PQTRANS_IDLE != 0) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PGTransactionStatusType", "PQTRANS_IDLE", (int)PQTRANS_IDLE, 0);
    return -1;
  }
  if (PQTRANS_ACTIVE != 1) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PGTransactionStatusType", "PQTRANS_ACTIVE", (int)PQTRANS_ACTIVE, 1);
    return -1;
  }
  if (PQTRANS_INTRANS != 2) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PGTransactionStatusType", "PQTRANS_INTRANS", (int)PQTRANS_INTRANS, 2);
    return -1;
  }
  if (PQTRANS_INERROR != 3) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PGTransactionStatusType", "PQTRANS_INERROR", (int)PQTRANS_INERROR, 3);
    return -1;
  }
  if (PQTRANS_UNKNOWN != 4) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PGTransactionStatusType", "PQTRANS_UNKNOWN", (int)PQTRANS_UNKNOWN, 4);
    return -1;
  }
  return 0;
}

int _cffi_f_PQconnectPoll(PGconn*  x0)
{
  return PQconnectPoll(x0);
}

char*  _cffi_f_PQcmdStatus(PGresult*  x0)
{
  return PQcmdStatus(x0);
}

int _cffi_f_PQrequestCancel(PGconn*  x0)
{
  return PQrequestCancel(x0);
}

char const *  _cffi_f_PQparameterStatus(PGconn const *  x0, char const *  x1)
{
  return PQparameterStatus(x0, x1);
}

int _cffi_f_PQgetisnull(PGresult const *  x0, int x1, int x2)
{
  return PQgetisnull(x0, x1, x2);
}

int _cffi_f_PQnfields(PGresult const *  x0)
{
  return PQnfields(x0);
}

int _cffi_f_lo_lseek(PGconn*  x0, int x1, int x2, int x3)
{
  return lo_lseek(x0, x1, x2, x3);
}

int _cffi_f_PQfsize(PGresult const *  x0, int x1)
{
  return PQfsize(x0, x1);
}

PGcancel*  _cffi_f_PQgetCancel(PGconn*  x0)
{
  return PQgetCancel(x0);
}

unsigned char*  _cffi_f_PQescapeBytea(unsigned char const *  x0, unsigned long x1, unsigned long*  x2)
{
  return PQescapeBytea(x0, x1, x2);
}

int _cffi_f_PQstatus(PGconn const *  x0)
{
  return PQstatus(x0);
}

unsigned int _cffi_f_PQftype(PGresult const *  x0, int x1)
{
  return PQftype(x0, x1);
}

int _cffi_f_PQntuples(PGresult const *  x0)
{
  return PQntuples(x0);
}

char*  _cffi_f_PQgetvalue(PGresult const *  x0, int x1, int x2)
{
  return PQgetvalue(x0, x1, x2);
}

int _cffi_f_PQflush(PGconn*  x0)
{
  return PQflush(x0);
}

unsigned char*  _cffi_f_PQunescapeBytea(unsigned char const *  x0, unsigned long*  x1)
{
  return PQunescapeBytea(x0, x1);
}

int _cffi_e__PostgresPollingStatusType(char *out_error)
{
  if (PGRES_POLLING_FAILED != 0) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PostgresPollingStatusType", "PGRES_POLLING_FAILED", (int)PGRES_POLLING_FAILED, 0);
    return -1;
  }
  if (PGRES_POLLING_READING != 1) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PostgresPollingStatusType", "PGRES_POLLING_READING", (int)PGRES_POLLING_READING, 1);
    return -1;
  }
  if (PGRES_POLLING_WRITING != 2) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PostgresPollingStatusType", "PGRES_POLLING_WRITING", (int)PGRES_POLLING_WRITING, 2);
    return -1;
  }
  if (PGRES_POLLING_OK != 3) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PostgresPollingStatusType", "PGRES_POLLING_OK", (int)PGRES_POLLING_OK, 3);
    return -1;
  }
  if (PGRES_POLLING_ACTIVE != 4) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "PostgresPollingStatusType", "PGRES_POLLING_ACTIVE", (int)PGRES_POLLING_ACTIVE, 4);
    return -1;
  }
  return 0;
}

unsigned int _cffi_f_PQoidValue(PGresult const *  x0)
{
  return PQoidValue(x0);
}

int _cffi_e__ConnStatusType(char *out_error)
{
  if (CONNECTION_OK != 0) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_OK", (int)CONNECTION_OK, 0);
    return -1;
  }
  if (CONNECTION_BAD != 1) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_BAD", (int)CONNECTION_BAD, 1);
    return -1;
  }
  if (CONNECTION_STARTED != 2) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_STARTED", (int)CONNECTION_STARTED, 2);
    return -1;
  }
  if (CONNECTION_MADE != 3) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_MADE", (int)CONNECTION_MADE, 3);
    return -1;
  }
  if (CONNECTION_AWAITING_RESPONSE != 4) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_AWAITING_RESPONSE", (int)CONNECTION_AWAITING_RESPONSE, 4);
    return -1;
  }
  if (CONNECTION_AUTH_OK != 5) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_AUTH_OK", (int)CONNECTION_AUTH_OK, 5);
    return -1;
  }
  if (CONNECTION_SETENV != 6) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_SETENV", (int)CONNECTION_SETENV, 6);
    return -1;
  }
  if (CONNECTION_SSL_STARTUP != 7) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_SSL_STARTUP", (int)CONNECTION_SSL_STARTUP, 7);
    return -1;
  }
  if (CONNECTION_NEEDED != 8) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ConnStatusType", "CONNECTION_NEEDED", (int)CONNECTION_NEEDED, 8);
    return -1;
  }
  return 0;
}

char*  _cffi_f_PQfname(PGresult const *  x0, int x1)
{
  return PQfname(x0, x1);
}

int _cffi_f_lo_close(PGconn*  x0, int x1)
{
  return lo_close(x0, x1);
}

PGresult*  _cffi_f_PQexec(PGconn*  x0, char const *  x1)
{
  return PQexec(x0, x1);
}

void _cffi_f_PQfreeCancel(PGcancel*  x0)
{
  PQfreeCancel(x0);
}

int _cffi_f_PQcancel(PGcancel*  x0, char*  x1, int x2)
{
  return PQcancel(x0, x1, x2);
}

int _cffi_f_PQgetCopyData(PGconn*  x0, char* *  x1, int x2)
{
  return PQgetCopyData(x0, x1, x2);
}

PGconn*  _cffi_f_PQconnectStart(char const *  x0)
{
  return PQconnectStart(x0);
}

int _cffi_f_lo_tell(PGconn*  x0, int x1)
{
  return lo_tell(x0, x1);
}

int _cffi_f_PQsendQuery(PGconn*  x0, char const *  x1)
{
  return PQsendQuery(x0, x1);
}

unsigned int _cffi_f_lo_create(PGconn*  x0, unsigned int x1)
{
  return lo_create(x0, x1);
}

int _cffi_f_PQtransactionStatus(PGconn const *  x0)
{
  return PQtransactionStatus(x0);
}

PGresult*  _cffi_f_PQgetResult(PGconn*  x0)
{
  return PQgetResult(x0);
}

int _cffi_e__ExecStatusType(char *out_error)
{
  if (PGRES_EMPTY_QUERY != 0) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_EMPTY_QUERY", (int)PGRES_EMPTY_QUERY, 0);
    return -1;
  }
  if (PGRES_COMMAND_OK != 1) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_COMMAND_OK", (int)PGRES_COMMAND_OK, 1);
    return -1;
  }
  if (PGRES_TUPLES_OK != 2) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_TUPLES_OK", (int)PGRES_TUPLES_OK, 2);
    return -1;
  }
  if (PGRES_COPY_OUT != 3) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_COPY_OUT", (int)PGRES_COPY_OUT, 3);
    return -1;
  }
  if (PGRES_COPY_IN != 4) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_COPY_IN", (int)PGRES_COPY_IN, 4);
    return -1;
  }
  if (PGRES_BAD_RESPONSE != 5) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_BAD_RESPONSE", (int)PGRES_BAD_RESPONSE, 5);
    return -1;
  }
  if (PGRES_NONFATAL_ERROR != 6) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_NONFATAL_ERROR", (int)PGRES_NONFATAL_ERROR, 6);
    return -1;
  }
  if (PGRES_FATAL_ERROR != 7) {
    snprintf(out_error, 255, "in enum %s: %s has the real value %d, not %d",
            "ExecStatusType", "PGRES_FATAL_ERROR", (int)PGRES_FATAL_ERROR, 7);
    return -1;
  }
  return 0;
}

unsigned long _cffi_f_PQescapeStringConn(PGconn*  x0, char*  x1, char const *  x2, unsigned long x3, int*  x4)
{
  return PQescapeStringConn(x0, x1, x2, x3, x4);
}

int _cffi_f_lo_read(PGconn*  x0, int x1, char*  x2, unsigned long x3)
{
  return lo_read(x0, x1, x2, x3);
}

char*  _cffi_f_PQresultErrorField(PGresult const *  x0, int x1)
{
  return PQresultErrorField(x0, x1);
}

int _cffi_f_PQconsumeInput(PGconn*  x0)
{
  return PQconsumeInput(x0);
}

int _cffi_f_PQbackendPID(PGconn const *  x0)
{
  return PQbackendPID(x0);
}

int _cffi_f_PQfmod(PGresult const *  x0, int x1)
{
  return PQfmod(x0, x1);
}

void _cffi_f_PQclear(PGresult*  x0)
{
  PQclear(x0);
}

unsigned int _cffi_f_lo_import(PGconn*  x0, char const *  x1)
{
  return lo_import(x0, x1);
}

int _cffi_f_lo_truncate(PGconn*  x0, int x1, unsigned long x2)
{
  return lo_truncate(x0, x1, x2);
}

int _cffi_f_lo_unlink(PGconn*  x0, unsigned int x1)
{
  return lo_unlink(x0, x1);
}

int _cffi_f_PQisBusy(PGconn*  x0)
{
  return PQisBusy(x0);
}

int _cffi_f_PQsetnonblocking(PGconn*  x0, int x1)
{
  return PQsetnonblocking(x0, x1);
}

unsigned long _cffi_f_PQescapeString(char*  x0, char const *  x1, unsigned long x2)
{
  return PQescapeString(x0, x1, x2);
}

char*  _cffi_f_PQresultErrorMessage(PGresult const *  x0)
{
  return PQresultErrorMessage(x0);
}

int _cffi_f_PQprotocolVersion(PGconn const *  x0)
{
  return PQprotocolVersion(x0);
}

int _cffi_f_PQgetlength(PGresult const *  x0, int x1, int x2)
{
  return PQgetlength(x0, x1, x2);
}

PGconn*  _cffi_f_PQconnectdb(char const *  x0)
{
  return PQconnectdb(x0);
}

int _cffi_f_PQputCopyEnd(PGconn*  x0, char const *  x1)
{
  return PQputCopyEnd(x0, x1);
}

int _cffi_f_lo_open(PGconn*  x0, unsigned int x1, int x2)
{
  return lo_open(x0, x1, x2);
}

int _cffi_f_PQputCopyData(PGconn*  x0, char const *  x1, int x2)
{
  return PQputCopyData(x0, x1, x2);
}

void _cffi_f_PQfinish(PGconn*  x0)
{
  PQfinish(x0);
}

int _cffi_f_lo_write(PGconn*  x0, int x1, char const *  x2, unsigned long x3)
{
  return lo_write(x0, x1, x2, x3);
}

char*  _cffi_f_PQerrorMessage(PGconn const *  x0)
{
  return PQerrorMessage(x0);
}

unsigned char*  _cffi_f_PQescapeByteaConn(PGconn*  x0, unsigned char const *  x1, unsigned long x2, unsigned long*  x3)
{
  return PQescapeByteaConn(x0, x1, x2, x3);
}

int _cffi_f_PQresultStatus(PGresult const *  x0)
{
  return PQresultStatus(x0);
}

void(* _cffi_f_PQsetNoticeProcessor(PGconn*  x0, void(* x1)(void* , char const * ), void*  x2))(void* , char const * )
{
  return PQsetNoticeProcessor(x0, x1, x2);
}

char*  _cffi_f_PQcmdTuples(PGresult*  x0)
{
  return PQcmdTuples(x0);
}

void _cffi_f_PQfreemem(void*  x0)
{
  PQfreemem(x0);
}

int _cffi_f_lo_export(PGconn*  x0, unsigned int x1, char const *  x2)
{
  return lo_export(x0, x1, x2);
}

PGnotify*  _cffi_f_PQnotifies(PGconn*  x0)
{
  return PQnotifies(x0);
}

static void _cffi_check_struct_pgNotify(struct pgNotify *p)
{
  /* only to generate compile-time warnings or errors */
  { char* (*tmp) = &p->relname; (void)tmp; }
  (void)((p->be_pid) << 1);
  { char* (*tmp) = &p->extra; (void)tmp; }
}
ssize_t _cffi_layout_struct_pgNotify(ssize_t i)
{
  struct _cffi_aligncheck { char x; struct pgNotify y; };
  static ssize_t nums[] = {
    sizeof(struct pgNotify),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct pgNotify, relname),
    sizeof(((struct pgNotify *)0)->relname),
    offsetof(struct pgNotify, be_pid),
    sizeof(((struct pgNotify *)0)->be_pid),
    offsetof(struct pgNotify, extra),
    sizeof(((struct pgNotify *)0)->extra),
    -1
  };
  return nums[i];
  /* the next line is not executed, but compiled */
  _cffi_check_struct_pgNotify(0);
}

int _cffi_f_PQsocket(PGconn const *  x0)
{
  return PQsocket(x0);
}

