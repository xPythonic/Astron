#pragma once
#include "MessageDirector.h"
#include "net/NetworkClient.h"

class MDNetworkParticipant : public MDParticipantInterface, public NetworkClient
{
	public:
		MDNetworkParticipant(boost::asio::ip::tcp::socket *socket);
		virtual void handle_datagram(DatagramHandle dg, DatagramIterator &dgi);
	private:
		virtual void receive_datagram(DatagramHandle dg);
		virtual void receive_disconnect();
};
