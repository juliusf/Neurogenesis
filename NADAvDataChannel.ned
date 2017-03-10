// * --------------------------------------------------------------------------
// *
// *     //====//  //===== <===//===>  //====//
// *    //        //          //      //    //    SCTP Optimization Project
// *   //=====   //          //      //====//   ==============================
// *        //  //          //      //           University of Duisburg-Essen
// *  =====//  //=====     //      //
// *
// * --------------------------------------------------------------------------
// *
// *   Copyright (C) 2009-2011 by Thomas Dreibholz
// *
// *   This program is free software: you can redistribute it and/or modify
// *   it under the terms of the GNU General Public License as published by
// *   the Free Software Foundation, either version 3 of the License, or
// *   (at your option) any later version.
// *
// *   This program is distributed in the hope that it will be useful,
// *   but WITHOUT ANY WARRANTY; without even the implied warranty of
// *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// *   GNU General Public License for more details.
// *
// *   You should have received a copy of the GNU General Public License
// *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
// *
// *   Contact: dreibh@iem.uni-due.de

//package inet.examples.webrtc.rtp_v_datachannel;
@namespace(inet);

import inet.node.inet.*;
import inet.node.inet.Router;
import ned.DatarateChannel;
import ned.DelayChannel;
import ned.IdealChannel;
import inet.networklayer.configurator.ipv4.IPv4NetworkConfigurator;
import inet.networklayer.configurator.ipv4.MultihomedFlatNetworkConfigurator;
import inet.common.queue.IOutputQueue;
import inet.common.queue.DropTailQueue;
import inet.common.queue.FIFOQueue;
import inet.common.queue.REDDropper;
import inet.applications.netperfmeter.NetPerfMeterHost;


channel coreChannel extends DatarateChannel
{

    @defaultname(coreChannel);
    int netID = default(1);
    datarate = default(1.0 Mbps);
    delay = default(20ms);
    ber = default(0);
    per = default(0);
    @display("ls=black,3");
}

channel accessChannel extends DatarateChannel
{
    int netID = default(1);
    datarate = default(1000 Mbps);
    delay = default(0ms);
    ber = default(0);
    per = default(0);
    @display("ls=blue,5");
}


network rtp_v_datachannel
{
    // ====== System Parameters =============================================
    parameters:
        int rtp_systems = default(0);
        bool testing = default(false);
        int algorithm = default(0);
        @display("bgi=maps/world,s;bgb=712,431");

        int netPerfMeterSystems = default(1);

    // ====== Network Components ============================================
    submodules:
        configurator: IPv4NetworkConfigurator {
            parameters:
                @display("p=850,75;i=abstract/penguin_l,gold");
        }

        // ------ Routers -----------------------------------------------------
        westernCoreRouter: StandardHost {
            parameters:
                forwarding = true;
                @display("p=219,172,c,150;i=abstract/router_l,gold");
            gates:
                pppg[2];
        }
        easternCoreRouter: StandardHost {
            parameters:
                forwarding = true;
                @display("p=402,163,c,150;i=abstract/router_l,gold");
            gates:
                pppg[2];
        }
        // ------ Systems -----------------------------------------------------
        rtcWebClient: SimpleRTCWebHost {
            parameters:
                forwarding = false;
                @display("p=93,326;i=device/laptop");
            gates:
                pppg[1];
        }
        rtcWebServer: SimpleRTCWebHost {
            parameters:
                forwarding = false;
                @display("p=635,262;i=device/server2");
            gates:
                pppg[1];
        }

    // ====== Connections ====================================================
    connections:

        westernCoreRouter.pppg[0] <--> coreChannel { @display("ls=blue,3");  } <--> easternCoreRouter.pppg[0];
        rtcWebClient.pppg[0] <--> accessChannel { @display("ls=green,5"); } <--> westernCoreRouter.pppg++;
        rtcWebServer.pppg[0] <--> accessChannel { @display("ls=green,5"); } <--> easternCoreRouter.pppg++;
}
