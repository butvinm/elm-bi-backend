#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "refal05rts.h"


enum { SOCKET_LIMIT = 40 };


static int s_sockets[SOCKET_LIMIT] = { 0 };


static struct sockaddr_in* s_addresses[SOCKET_LIMIT] = { NULL };


static void ensure_close_socket(unsigned int socket_no);


/*
Wrapper for the sys/socket.h#socket.

extern int socket (int __domain, int __type, int __protocol) __THROW;

<Socket-Open s.SocketNo s.Domain s.Type s.Protocol> == []
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Open, "Socket-Open") {
  struct r05_node *sSocketNo, *sDomain, *sType, *sProtocol;
  unsigned int socket_no;
  int domain, type, protocol;
  if (
    ! r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag
    || ! r05_svar_left(&sDomain, sSocketNo, arg_end) || R05_DATATAG_NUMBER != sDomain->tag
    || ! r05_svar_left(&sType, sDomain, arg_end) || R05_DATATAG_NUMBER != sType->tag
    || ! r05_svar_left(&sProtocol, sType, arg_end) || R05_DATATAG_NUMBER != sProtocol->tag
  ) {
    r05_recognition_impossible();
  }
  domain = sDomain->info.number;
  type = sType->info.number;
  protocol = sProtocol->info.number;

  socket_no = sSocketNo->info.number % SOCKET_LIMIT;
  ensure_close_socket(socket_no);

  int socket_fd = socket(domain, type, protocol);
  if (socket_fd < 0) {
    r05_builtin_error_errno("Failed to open socket");
  }
  s_sockets[socket_no] = socket_fd;

  r05_splice_to_freelist(arg_begin, arg_end);
}


/*
Close socket initialized with <Socket>

<Socket-Close s.SocketNo> == []
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Close, "Socket-Close") {
  struct r05_node *sSocketNo;
  unsigned int socket_no;
  if (! r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag) {
    r05_recognition_impossible();
  }

  socket_no = sSocketNo->info.number % SOCKET_LIMIT;
  ensure_close_socket(socket_no);

  r05_splice_to_freelist(arg_begin, arg_end);
}

static void ensure_close_socket(unsigned int socket_no) {
  if (s_sockets[socket_no] > 0) {
    close(s_sockets[socket_no]);
  }
  s_sockets[socket_no] = -1;
}


static void ensure_deinit_address(unsigned int address_no);


/*
Constructor for the linux/in.h#sockaddr_in

<Socket-InitAddress s.AddressNo s.Family s.Addr s.Port> == []
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_InitAddress, "Socket-InitAddress") {
  struct r05_node *sAddressNo, *sFamily, *sPort, *sAddr;
  unsigned int address_no;
  int family, port, addr;
  if (
    ! r05_svar_left(&sAddressNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sAddressNo->tag
    || ! r05_svar_left(&sFamily, sAddressNo, arg_end) || R05_DATATAG_NUMBER != sFamily->tag
    || ! r05_svar_left(&sAddr, sFamily, arg_end) || R05_DATATAG_NUMBER != sAddr->tag
    || ! r05_svar_left(&sPort, sAddr, arg_end) || R05_DATATAG_NUMBER != sPort->tag
  ) {
    r05_recognition_impossible();
  }

  address_no = sAddressNo->info.number % SOCKET_LIMIT;
  ensure_deinit_address(address_no);

  struct sockaddr_in* address = calloc(1, sizeof(struct sockaddr_in));
  address->sin_family = sFamily->info.number;
  address->sin_addr.s_addr = sAddr->info.number;
  address->sin_port = htons(sPort->info.number);
  s_addresses[address_no] = address;

  r05_splice_to_freelist(arg_begin, arg_end);
}


/*
Destructor for address created with <Socket-InitAddress>

<Socket-DeinitAddress s.AddressNo>
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_DeinitAddress, "Socket-DeinitAddress") {
  struct r05_node *sAddressNo;
  unsigned int address_no;

  if (! r05_svar_left(&sAddressNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sAddressNo->tag) {
    r05_recognition_impossible();
  }

  address_no = sAddressNo->info.number % SOCKET_LIMIT;
  ensure_deinit_address(address_no);

  r05_splice_to_freelist(arg_begin, arg_end);
}


static void ensure_deinit_address(unsigned int address_no) {
  free(s_addresses[address_no]);
  s_addresses[address_no] = NULL;
}


/*
Wrapper for the sys/socket.h#bind.

extern int bind (int __fd, __CONST_SOCKADDR_ARG __addr, socklen_t __len) __THROW;


    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("[ERROR] Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

<Socket-Bind s.ServerNo s.AddressNo>
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Bind, "Socket-Bind") {
  struct r05_node *sSocketNo, *sAddressNo;
  unsigned int socket_no, address_no;
  if (
    ! r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag
    || ! r05_svar_left(&sAddressNo, sSocketNo, arg_end) || R05_DATATAG_NUMBER != sAddressNo->tag
  ) {
    r05_recognition_impossible();
  }

  socket_no = sSocketNo->info.number % SOCKET_LIMIT;
  address_no = sAddressNo->info.number % SOCKET_LIMIT;

  int socket_fd = s_sockets[socket_no];
  if (socket_fd <= 0) {
    r05_builtin_error("Socket is not opened");
  }

  struct sockaddr_in* address = s_addresses[address_no];
  if (address == NULL) {
    r05_builtin_error("Address is not initialized");
  }

  if (bind(socket_fd, (struct sockaddr*)address, sizeof(*address)) < 0) {
    r05_builtin_error_errno("Failed to bind socket");
  }

  r05_splice_to_freelist(arg_begin, arg_end);
}


/*
Wrapper for the sys/socket.h#listen.

extern int listen (int __fd, int __n) __THROW;

<Socket-Listen s.SocketNo s.RequestLimit>
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Listen, "Socket-Listen") {
  struct r05_node *sSocketNo, *sRequestLimit;
  unsigned int socket_no;
  int request_limit;

  if (
      !r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag
      || !r05_svar_left(&sRequestLimit, sSocketNo, arg_end) || R05_DATATAG_NUMBER != sRequestLimit->tag
  ) {
      r05_recognition_impossible();
  }

  socket_no = sSocketNo->info.number % SOCKET_LIMIT;
  request_limit = sRequestLimit->info.number;

  int socket_fd = s_sockets[socket_no];
  if (socket_fd <= 0) {
      r05_builtin_error("Socket is not opened");
  }

  if (listen(socket_fd, request_limit) < 0) {
      r05_builtin_error_errno("Failed to listen on socket");
  }

  r05_splice_to_freelist(arg_begin, arg_end);
}

/*
Wrapper for the sys/socket.h#accept.

extern int accept (int __fd, __SOCKADDR_ARG __addr, socklen_t *__restrict __addr_len);

<Socket-Accept s.SocketNo s.AddressNo> == s.ClientSocketNo
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Accept, "Socket-Accept") {
  struct r05_node *callee = arg_begin->next;
  struct r05_node *sSocketNo, *sAddressNo;
  unsigned int socket_no, address_no;

  if (
      !r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag
      || !r05_svar_left(&sAddressNo, sSocketNo, arg_end) || R05_DATATAG_NUMBER != sAddressNo->tag
  ) {
      r05_recognition_impossible();
  }

  socket_no = sSocketNo->info.number % SOCKET_LIMIT;
  address_no = sAddressNo->info.number % SOCKET_LIMIT;

  int server_fd = s_sockets[socket_no];
  if (server_fd <= 0) {
      r05_builtin_error("Socket is not opened");
  }

  struct sockaddr_in *address = s_addresses[address_no];
  if (address == NULL) {
      r05_builtin_error("Address is not initialized");
  }

  socklen_t addr_len = sizeof(struct sockaddr_in);
  int client_fd = accept(server_fd, (struct sockaddr *)address, &addr_len);
  if (client_fd <= 0) {
      r05_builtin_error_errno("Failed to accept connection");
  }

  r05_number client_socket_no = client_fd % SOCKET_LIMIT;
  ensure_close_socket(client_socket_no);
  s_sockets[client_socket_no] = client_fd;

  arg_begin->tag = R05_DATATAG_NUMBER;
  arg_begin->info.number = client_socket_no;
  r05_splice_to_freelist(callee, arg_end);
}


enum { MAX_BODY_SIZE = 4096 };

/*
Write to the socket.

<Socket-Write s.SocketNo e.Expr>
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Write, "Socket-Write") {
  char buffer[MAX_BODY_SIZE];
  size_t buffer_len = 0;

  struct r05_node *callee = arg_begin->next;
  struct r05_node *p, *before_expr;

  struct r05_node *sSocketNo;
  if (!r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag) {
    r05_recognition_impossible();
  }

  before_expr = sSocketNo;

  int socket_fd = s_sockets[sSocketNo->info.number];
  if (socket_fd <= 0) {
    r05_builtin_error("Socket is not opened");
  }

  for (p = before_expr->next; p != arg_end; p = p->next) {
    int len = 0;

    switch (p->tag) {
      case R05_DATATAG_CHAR:
        len = snprintf(buffer + buffer_len, MAX_BODY_SIZE - buffer_len, "%c", p->info.char_);
        break;

      case R05_DATATAG_FUNCTION:
        len = snprintf(buffer + buffer_len, MAX_BODY_SIZE - buffer_len, "%s ", p->info.function->name);
        break;

      case R05_DATATAG_NUMBER:
        len = snprintf(buffer + buffer_len, MAX_BODY_SIZE - buffer_len, "%lu ", (long unsigned int)p->info.number);
        break;

      case R05_DATATAG_OPEN_BRACKET:
        len = snprintf(buffer + buffer_len, MAX_BODY_SIZE - buffer_len, "(");
        break;

      case R05_DATATAG_CLOSE_BRACKET:
        len = snprintf(buffer + buffer_len, MAX_BODY_SIZE - buffer_len, ")");
        break;

      default:
        r05_switch_default_violation(p->tag);
    }

    if (len < 0 || len >= MAX_BODY_SIZE - buffer_len) {
      r05_builtin_error("Buffer overflow during formatting");
    }

    buffer_len += len;

    if (buffer_len >= MAX_BODY_SIZE - 1) {
      if (write(socket_fd, buffer, buffer_len) == -1) {
        r05_builtin_error_errno("Error writing to socket");
      }
      buffer_len = 0;
    }
  }

  if (buffer_len > 0) {
    if (write(socket_fd, buffer, buffer_len) == -1) {
      r05_builtin_error_errno("Error writing to socket");
    }
  }

  r05_splice_to_freelist(arg_begin, arg_end);
}


/*
Read the socket.

<Socket-Read s.SocketNo> = e.Expr
*/
R05_DEFINE_ENTRY_FUNCTION(Socketm_Read, "Socket-Read") {
  struct r05_node *sSocketNo;
  if (!r05_svar_left(&sSocketNo, arg_begin->next, arg_end) || R05_DATATAG_NUMBER != sSocketNo->tag) {
    r05_recognition_impossible();
  }

  int socket_fd = s_sockets[sSocketNo->info.number];
  if (socket_fd <= 0) {
    r05_builtin_error("Socket is not opened");
  }

  char buffer[MAX_BODY_SIZE];
  size_t buffer_len = read(socket_fd, buffer, sizeof(buffer) - 1);
  if (buffer_len >= MAX_BODY_SIZE) {
      r05_builtin_error("Buffer overflow while reading from socket");
  }
  buffer[buffer_len] = '\0';

  r05_reset_allocator();
  r05_alloc_string(buffer);
  r05_splice_from_freelist(arg_begin);
  r05_splice_to_freelist(arg_begin, arg_end);
}
