# MUD Runtime.
 #-
 # Copyright (c) 2013 Clint Banis (hereby known as "The Author")
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 # 3. All advertising materials mentioning features or use of this software
 #    must display the following acknowledgement:
 #        This product includes software developed by The Author, Clint Banis.
 # 4. The name of The Author may not be used to endorse or promote products
 #    derived from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
 # ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 # BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 # CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
from .events import *
from .structure import *

import registry

# Todo: Perform object registration later during boot cycle.
#@runtime.MUD.Runtime.API
class MudRuntime(registry.Access):
    # This could be documented much better:
    # ---
    # Represents the main access object for mud runtime layer.
    # Utilizes registry access base class for addressing the
    #    named object directory.
    #
    # The actual instance is created by registry subroutines.
    # Should probably be a Singleton.
    pass

# Event Names.
EVENT_NAMES = ['bootStart'                  ,'bootComplete'               ,
               'resetStart'                 ,'resetComplete'              ,
               'greetPlayer'                ,'welcomePlayer'              ,
               'makePrompt'                 ,'loadPlayerStore'            ,
               'playerSavePoint'            ,'startRentSave'              ,
               'completeRentSave'           ,'startRentLoad'              ,
               'completeRentLoad'           ,'deleteRentFile'             ,
               'idleToVoid'                 ,'timedOut'                   ,
               'helpQueryNotFound'          ,'helpQueryUnfinished'        ,
               'helpQueryComplete'          ,'doPython'                   ,
               'createItemPrototype'        ,'createItemInstance'         ,
               'extractItemInstance'        ,'createMobilePrototype'      ,
               'createMobileInstance'       ,'extractMobileInstance'      ,
               'movement'                   ,'dealDamage'                 ,
               'slayMobile'                 ,'purgeMobile'                ,
               'deathTrap'                  ,'createRoom'                 ,
               'startZoneReset'             ,'endZoneReset'               ,
               'itemToRoom'                 ,'itemFromRoom'               ,
               'itemToContainer'            ,'itemFromContainer'          ,
               'itemToCarrier'              ,'itemFromCarrier'            ,
               'mobileToRoom'               ,'mobileFromRoom'             ,
               'lookAtRoom'                 ,'firstSpecial'               ,
               'lastSpecial'                ,'mudlog'                     ,
               'telnetCommand'              ,'writeItemPrototypeStart'    ,
               'writeItemPrototypeComplete' ,'startSpellAssign'           ,
               'startSkillAssign'           ,'newConnection'              ,
               'disconnection'              ,'enterGame'                  ,
               'quitGame'                   ,'newPlayer'                  ,
               'loadZone'                   ,'createZone'                 ,
               'castSpellSuperior'          ,'startSpellCast'             ,
               'completeSpellCast'          ,'callMagic'                  ,
               'saySpell'                   ,'lookupSkill'                ,
               'setSpellLevel'              ,'sendMail'                   ,
               'switchCutBy'                ,'unswitchForcedBy'           ,
               'usurpedBy'                  ,'duplicateKilledBy'          ,
               'reconnection'               ,'usurped'                    ,
               'passwordChange'             ,'shutdownGame'               ,
               'playerInput'                ,'playerActivation'           ]

BINDINGS = \
    """
    [MemberResolution]
     # The heartbeat object is implemented directly, not as a binding.
     #  (see mud.installBridge)
     # heartbeat                   world.heartbeat.pulse # (Bridge Module)

     doPython                    mud.player.doPython
     newConnection               mud.player.interpret

     login                       mud.player.login
     enterGame                   mud.player.enterGame

     newPlayer                   mud.player.newPlayer

     greetPlayer                 mud.player.greetPlayer
     welcomePlayer               mud.player.welcomePlayer

     lookAtRoom                  mud.player.lookAtRoom

     makePrompt                  mud.player.shell.makePrompt

     telnetCommand               mud.player.telnet.process_command

     # writeItemPrototypeStart     mud.zones.olc.writeItemPrototypeStart
     # writeItemPrototypeComplete  mud.zones.olc.writeItemPrototypeComplete

    ## playerSavePoint           mud.player.db.playerSavePoint
    ## loadPlayerStore           mud.player.db.loadPlayerStore

    ## deleteRentFile            mud.deleteRentFile

    ## createMobileInstance      zones.MobileCreation
    ## createItemInstance        zones.ItemCreation

    [Logging]
    ##     quitGame                
    ##     disconnection           
    ##     idleToVoid              
    ##     timedOut                
    ##
    ##     helpQueryNotFound       
    ##     helpQueryUnfinished     
    ##     helpQueryComplete       
    ##
    ##     startRentSave           
    ##     completeRentSave        
    ##     startRentLoad
    ##     completeRentLoad
    ##
    ##    ## extractMobileInstance   
    ##    ## extractItemInstance     
    ##
    ##    ## startZoneReset          
    ##    ## endZoneReset            
    ##
    ##     createMobilePrototype   
    ##     createItemPrototype     
    ##     createZone              
    ##     createRoom              
    ##
    ##    ## movement                
    ##    ## dealDamage              
    ##
    ##     slayMobile              
    ##     purgeMobile             
    ##     deathTrap               
    ##
    ##     startSpellAssign
    ##     telnetCommand
    """
