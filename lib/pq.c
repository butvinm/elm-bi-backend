#include <stdio.h>
#include <libpq-fe.h>

#include "refal05rts.h"


enum { CONNECTIONS_LIMIT = 69 };

static PGconn *conns[CONNECTIONS_LIMIT] = { NULL };

enum { MAX_CONNINFO_LEN = 1024 };

/**
Create connection to the database (PQconnectdb).

<PQ-ConnectDB e.ConnInfo> == s.ConnNo
*/
R05_DEFINE_ENTRY_FUNCTION(PQm_ConnectDB, "PQ-ConnectDB") {
  struct r05_node *sConnNo;
  sConnNo = arg_begin;

  struct r05_node *callee = arg_begin->next;
  struct r05_node *p = callee->next;

  char conninfo[MAX_CONNINFO_LEN];
  size_t conninfo_len = 0;
  while (p != arg_end) {
    if (p->tag == R05_DATATAG_CHAR) {
      conninfo[conninfo_len++] = p->info.char_;
    }
    p = p->next;
  }
  conninfo[conninfo_len] = '\0';

  size_t free_conn = CONNECTIONS_LIMIT;
  for (size_t i = 0; i < CONNECTIONS_LIMIT; ++i) {
    if (conns[i] == NULL) {
      free_conn = i;
      break;
    }
  }
  if (free_conn == CONNECTIONS_LIMIT) {
    r05_builtin_error("CONNECTIONS_LIMIT exceeded");
  }
  conns[free_conn] = PQconnectdb(conninfo);

  sConnNo->tag = R05_DATATAG_NUMBER;
  sConnNo->info.number = free_conn;

  r05_splice_to_freelist(sConnNo->next, arg_end);
}


unsigned int get_conn_no(struct r05_node *arg_begin, struct r05_node *arg_end) {
  struct r05_node *sConnNo;
  unsigned int conn_no;
  if (! r05_svar_left(&sConnNo, arg_begin->next, arg_end) || (R05_DATATAG_NUMBER != sConnNo->tag)) {
    r05_recognition_impossible();
  }

  conn_no = sConnNo->info.number % CONNECTIONS_LIMIT;
  if (conns[conn_no] == NULL) {
    r05_builtin_error("Connection with specified s.ConnNo is not initialized");
  }

  return conn_no;
}


/**
Finish the connection (PQfinish)

<PQ-Finish s.ConnNo> == []
*/
R05_DEFINE_ENTRY_FUNCTION(PQm_Finish, "PQ-Finish") {
  unsigned int conn_no = get_conn_no(arg_begin, arg_end);

  PQfinish(conns[conn_no]);
  conns[conn_no] = NULL;

  r05_splice_to_freelist(arg_begin, arg_end);
}



/**
Get connection status (PQstatus).

<PQ-Status s.ConnNo> = s.Status

s.Status ::=
  | 0  // CONNECTION_OK
	| 1  // CONNECTION_BAD
	| 2  // CONNECTION_STARTED
	| 3  // CONNECTION_MADE
	| 4  // CONNECTION_AWAITING_RESPONSE
	| 5  // CONNECTION_AUTH_OK
	| 6  // CONNECTION_SETENV
	| 7  // CONNECTION_SSL_STARTUP
	| 8  // CONNECTION_NEEDED
	| 9  // CONNECTION_CHECK_WRITABLE
	| 10  // CONNECTION_CONSUME
	| 11  // CONNECTION_GSS_STARTUP
	| 12  // CONNECTION_CHECK_TARGET
	| 13  // CONNECTION_CHECK_STANDBY
*/
R05_DEFINE_ENTRY_FUNCTION(PQm_Status, "PQ-Status") {
  struct r05_node *sStatus;
  sStatus = arg_begin;

  unsigned int conn_no = get_conn_no(arg_begin, arg_end);

  ConnStatusType status = PQstatus(conns[conn_no]);

  sStatus->tag = R05_DATATAG_NUMBER;
  sStatus->info.number = status;

  r05_splice_to_freelist(sStatus->next, arg_end);
}


/**
Get error message (PQerrorMessage).

<PQ-ErrorMessage s.ConnNo> == e.Message
*/
R05_DEFINE_ENTRY_FUNCTION(PQm_ErrorMessage, "PQ-ErrorMessage") {
  unsigned int conn_no = get_conn_no(arg_begin, arg_end);

  char *error_message = PQerrorMessage(conns[conn_no]);

  r05_reset_allocator();
  r05_alloc_string(error_message);
  r05_splice_from_freelist(arg_begin);
  r05_splice_to_freelist(arg_begin, arg_end);
}


enum { MAX_QUERY_LEN = 4096 };

/**
Execute SQL command and fetch result (PQexec).

<PQ-ExecFetch s.ConnNo e.Query> == s.Status [] | 2 t.Tuple*
t.Tuples ::= (t.Field*)
t.Field ::= (s.CHAR*)

0 [] - Got unexpected query result. Use <PQ-ErrorMessage s.ConnNo> to get the reason.
1 t.Tuple* - Tuples with data of the successful query result (2 is PGRES_TUPLES_OK).
*/
R05_DEFINE_ENTRY_FUNCTION(PQm_ExecFetch, "PQ-ExecFetch") {
  unsigned int conn_no = get_conn_no(arg_begin, arg_end);

  struct r05_node *callee = arg_begin->next;
  struct r05_node *p = callee->next;

  char query[MAX_QUERY_LEN];
  size_t query_len = 0;
  while (p != arg_end) {
    if (p->tag == R05_DATATAG_CHAR) {
      query[query_len++] = p->info.char_;
    }
    p = p->next;
  }
  query[query_len] = '\0';

  PGresult *res = PQexec(conns[conn_no], query);

  ExecStatusType status = PQresultStatus(res);
  if (status != PGRES_TUPLES_OK) {
    struct r05_node *sStatus = arg_begin;
    sStatus->tag = R05_DATATAG_NUMBER;
    sStatus->info.number = status;
    PQclear(res);
    r05_splice_to_freelist(sStatus->next, arg_end);
    return;
  }

  struct r05_node *tuple_left_bracket, *tuple_right_bracket, *field_left_bracket, *field_right_bracket;

  r05_reset_allocator();
  r05_alloc_number(status);

  for (int i = 0; i < PQntuples(res); i++) {
    r05_alloc_open_bracket(&tuple_left_bracket);
    for (int j = 0; j < PQnfields(res); j++) {
      r05_alloc_open_bracket(&field_left_bracket);
      r05_alloc_string(PQgetvalue(res, i, j));
      r05_alloc_close_bracket(&field_right_bracket);
      r05_link_brackets(field_left_bracket, field_right_bracket);
    }
    r05_alloc_close_bracket(&tuple_right_bracket);
    r05_link_brackets(tuple_left_bracket, tuple_right_bracket);
  }

  PQclear(res);

  r05_splice_from_freelist(arg_begin);
  r05_splice_to_freelist(arg_begin, arg_end);
}
