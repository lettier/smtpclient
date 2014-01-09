'''

David Lettier (C) 2014.

http://www.lettier.com/

Needs:

	- DNSPython http://www.dnspython.org/
		- $ sudo easy_install dnspython

	- Python 2.7

'''

import dns.resolver; # DNS resolution.
import operator; # Sorting.
import sys;
import socket;
import ssl; # For TLS authentication.
import base64; # Base 64 encoding.

# Get the email parameters.

print "\r\nWelcome to Emailer 5000!\r\n";

to_email      = raw_input( "To:   " );
from_email    = raw_input( "From: " );
email_subject = raw_input( "Subject: " );
email_message = raw_input( "Message: " );

# Ask if they want to try the vanilla SMTP on port 25.

use_mx_dns = raw_input( "\r\nUse MX records from DNS with port 25 (y/n/q): " );

while ( use_mx_dns.rstrip( ) != "y" and use_mx_dns.rstrip( ) != "n" and use_mx_dns.rstrip( ) != "q" ):
	
	print "\r\nI didn't get that...\r";
	
	use_mx_dns = raw_input( "\r\nUse MX records from DNS with port 25 (y/n/q): " );
	
if ( use_mx_dns.rstrip( ) == "q" ):
	
	print "\r\nOK, well...bye!\r\n";
	
	sys.exit( 0 );
	
to_email_domain  = None;

dns_query_answer = None;

smtp_servers     = [ ];
	
if ( use_mx_dns.rstrip( ) == "y" ):
	
	# Attempt to try the vanilla SMTP on port 25.
	
	# Get the MX records for the domain of the to email address.

	to_email_domain = to_email.split( "@" )[ -1 ];

	dns_query_answer = dns.resolver.query( to_email_domain, "MX" );

	i = 0

	for x in dns_query_answer:
		
		smtp_server_host_name = list( filter( None, dns_query_answer.rrset[ i ].exchange[ 0 : ] ) );
		
		smtp_servers.append( [ int( dns_query_answer.rrset[ i ].preference ), ".".join( smtp_server_host_name ) ] );
					
		i += 1
		
	# Sort by preference as per the MX records.
		
	smtp_servers.sort( key = operator.itemgetter( 0 ) );
	
	i = len( smtp_servers );
	
	j = 0;
	
	# Try each server in the MX record in order of preference.

	for server in smtp_servers:
		
		smtp_port = 25;
		
		smtp_server_host_name = server[ 1 ];

		client_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM );
		
		client_socket.settimeout( 10 );
		
		server_host_name_ip = socket.gethostbyname( server[ 1 ] );
		
		print "\r\nTrying for 10 seconds...\r\n";
	
		print smtp_server_host_name + " (" + str( server_host_name_ip ) + ":" + str( smtp_port ) + ")";
		
		try:
		
			client_socket.connect( ( server_host_name_ip, smtp_port ) );
			
		except socket.timeout:
			
			if ( j == i - 1 ):

				print "\r\nHmm...couldn't connect to any. Maybe your ISP is blocking port 25? Bye!\r\n";
				
				client_socket.close( );
				
				sys.exit( 0 );
				
			else:
				
				print "\r\nHmm...couldn't connect. Let's try the next one!\r\n";
			
				client_socket.close( );
				
				j = j + 1;
			
				continue;
		
		client_socket.settimeout( None );
		
		print "\r\nConnected!\r\n"
		
		# Get the greeting.
		
		data = client_socket.recv( 1024 );
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "220" ):
			
			print "\r\nOOPS...there was a problem. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );
			
		# Send the EHLO/HELO command.
		
		print "[CLIENT] HELO " + smtp_server_host_name + "\r\n";
		
		client_socket.send( "HELO " + smtp_server_host_name + "\r\n" );
		
		data = client_socket.recv( 1024 )
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "250" ):
			
			print "\r\nOOPS...there was a problem. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );	
			
		# Send the mail from address.
		
		print "[CLIENT] MAIL FROM:<" + from_email + ">\r\n";	
		
		client_socket.send( "MAIL FROM:<" + from_email + ">\r\n" );
		
		data = client_socket.recv( 1024 );
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "250" ):
			
			print "\r\nOOPS...there was a problem. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );
			
		# Send the receipt to address.
		
		print "[CLIENT] RCPT TO:<" + to_email + ">\r\n";
		
		client_socket.send( "RCPT TO:<" + to_email + ">\r\n" );
		
		data = client_socket.recv( 1024 );
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "250" ):
			
			print "\r\nOOPS...there was a problem. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );
			
		# Begin sending the message body.
		
		print "[CLIENT] DATA\r\n";
		
		client_socket.send( "DATA\r\n" );
		
		data = client_socket.recv( 1024 );
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "354" ):
			
			print "\r\nOOPS...there was a problem. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );

		print "[CLIENT] Subject:" + email_subject + "\r\n" + "From:" + from_email.rstrip( ) + "\r\n" + "To:" + to_email.rstrip( ) + "\r\n" + email_message + "\r\n.\r\n";
		
		client_socket.send( "Subject:" + email_subject + "\r\n" + "From:" + from_email.rstrip( ) + "\r\n" + "To:" + to_email.rstrip( ) + "\r\n" + email_message + "\r\n.\r\n" );
		
		data = client_socket.recv( 1024 );
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "250" ):
			
			print "\r\nOOPS...there was a problem. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );
			
		# End the message body.
		
		# Send the QUIT command.
		
		print "[CLIENT] QUIT\r\n";
		
		client_socket.send( "QUIT\r\n" );
		
		data = client_socket.recv( 1024 );
		
		print "[SERVER] " + data;
		
		if ( data.split( " " )[ 0 ] != "221" ):
			
			print "\r\nOOPS...there was a problem but the message should be sent. Bye!\r\n";
			
			client_socket.close( );
			
			sys.exit( 1 );
			
		# Message sent. Close socket.		
		
		print "Message sent...bye!\r\n";
		
		client_socket.close( );
		
		# If it got this far, don't try the next server.
		
		break;
		
else:
	
	# Try the TLS authentication method.
	
	# Get login parameters.
	
	print "\r\nOK, let us try authentication on port 587...\r\n";
	
	username = raw_input( "Username: " );
	
	print "\r\nIf you are using 2-factor authentication, you'll need to enter an application specific password.\r\n";
	
	password = raw_input( "Password: " );
	
	from_email_domain = from_email.split( "@" )[ -1 ];
	
	# Try to guess their TLS SMTP server.
	
	smtp_server_host_name = None;
	
	if ( from_email_domain == "gmail.com" ):
		
		smtp_server_host_name = "smtp.gmail.com";
		
	elif ( from_email_domain == "hotmail.com" ):
		
		smtp_server_host_name = "smtp.live.com";
		
	elif( from_email_domain == "yahoo.com" ):
		
		smtp_server_host_name = "smtp.mail.yahoo.com";
		
	else:
		
		# Ask them for the smtp server for their domain.
		
		print "\r\nI don't recognize this domain: " + str( from_email_domain ) + "\r\n";
		
		smtp_server_host_name = raw_input( "What is the outgoing SMTP server host name (for instance GMail's is smtp.gmail.com or Hotmail's is smtp.live.com): " );
	
	# Industry standard TLS SMTP port.
	
	smtp_port = 587;

	client_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM );
	
	# Try to connect for 10 seconds.
	
	client_socket.settimeout( 10 );
	
	server_host_name_ip = socket.gethostbyname( smtp_server_host_name );
	
	print "\r\nTrying for 10 seconds...\r\n";
	
	print smtp_server_host_name + " (" + str( server_host_name_ip ) + ":" + str( smtp_port ) + ")";
	
	try:
	
		client_socket.connect( ( server_host_name_ip, smtp_port ) );
		
	except socket.timeout:

		print "\r\nHmm...couldn't connect. Bye!\r\n";
		
		sys.exit( 1 );
	
	client_socket.settimeout( None );
	
	print "\r\nConnected!\r\n"
	
	# Get the greeting.
	
	data = client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "220" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		client_socket.close( );
		
		sys.exit( 1 );
		
	# Send the hello.
	
	print "[CLIENT] HELO " + smtp_server_host_name + "\r\n";
	
	client_socket.send( "HELO " + smtp_server_host_name + "\r\n" );
	
	data = client_socket.recv( 1024 )
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "250" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		client_socket.close( );
		
		sys.exit( 1 );
		
	# Start TLS authentication.
	
	print "[CLIENT] STARTTLS\r\n";
	
	client_socket.send( "STARTTLS\r\n" );
	
	data = client_socket.recv( 1024 )
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "220" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		client_socket.close( );
		
		sys.exit( 1 );
		
	# Wrap the vanilla client socket in a secure socket layer for the Transport Layer Security.
	
	ssl_client_socket = ssl.wrap_socket( client_socket, ssl_version = ssl.PROTOCOL_SSLv23 );
	
	# Send a hello again as the server must forget everything before the STARTTLS command.
	
	print "[CLIENT] HELO " + smtp_server_host_name + "\r\n";
	
	ssl_client_socket.send( "HELO " + smtp_server_host_name + "\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "250" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# Begin authentication.
	
	print "[CLIENT] AUTH LOGIN\r\n";
	
	ssl_client_socket.send( "AUTH LOGIN\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "334" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# Send the username in base 64.
	
	print "[CLIENT] " + str( base64.b64encode( username.rstrip( ) ) ) + "\r\n";
	
	ssl_client_socket.send( base64.b64encode( username.rstrip( ) ) + "\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "334" ):
		
		print "\r\nOOPS...there was a problem, maybe wrong username?. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# Send the password in base 64.
	
	print "[CLIENT] " + str( base64.b64encode( password.rstrip( ) ) ) + "\r\n";
	
	ssl_client_socket.send( base64.b64encode( password.rstrip( ) ) + "\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "235" ):
		
		print "\r\nOOPS...there was a problem, maybe wrong password? Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# End authentication.
	
	# Send the mail from address.
	
	print "[CLIENT] MAIL FROM:<" + from_email + ">\r\n";	
	
	ssl_client_socket.send( "MAIL FROM:<" + from_email + ">\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "250" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# Send the recipient address.
	
	print "[CLIENT] RCPT TO:<" + to_email + ">\r\n";
	
	ssl_client_socket.send( "RCPT TO:<" + to_email + ">\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "250" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# Begin sending message body.
	
	print "[CLIENT] DATA\r\n";
	
	ssl_client_socket.send( "DATA\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "354" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
	
	print "[CLIENT] Subject:" + email_subject + "\r\n" + "From:" + from_email.rstrip( ) + "\r\n" + "To:" + to_email.rstrip( ) + "\r\n" + email_message + "\r\n.\r\n";
	
	ssl_client_socket.send( "Subject:" + email_subject + "\r\n" + "From:" + from_email.rstrip( ) + "\r\n" + "To:" + to_email.rstrip( ) + "\r\n" + email_message + "\r\n.\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "250" ):
		
		print "\r\nOOPS...there was a problem. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
		
	# End message body.
	
	# Quit this session and close the socket.
	
	print "[CLIENT] QUIT\r\n";
	
	ssl_client_socket.send( "QUIT\r\n" );
	
	data = ssl_client_socket.recv( 1024 );
	
	print "[SERVER] " + data;
	
	if ( data.split( " " )[ 0 ] != "221" ):
		
		print "\r\nOOPS...there was a problem but the message should be sent. Bye!\r\n";
		
		ssl_client_socket.close( );
		
		sys.exit( 1 );
	
	ssl_client_socket.close( );
	
	print "Message sent...bye!\r\n";
	
# Exit the program.
	
sys.exit( 0 );
