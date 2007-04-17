#
# $Source$
# $Date$
# $Revision$
#
# DESCRIPTION:
# A dialog box for setting and editing a lineup
# 
# This file is part of Chadwick, a library for baseball play-by-play and stats
# Copyright (C) 2005-2007, Ted Turocy (drarbiter@gmail.com)
#
# This program is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License, or (at 
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License 
# for more details.
#
# You should have received a copy of the GNU General Public License along 
# with this program; if not, write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# 

import wx

class LineupDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)

        sizer = wx.BoxSizer(wx.VERTICAL)

        gridSizer = wx.FlexGridSizer(10)

        self.players = [ wx.Choice(self, wx.ID_ANY, size=(300, -1))
                         for i in range(10) ]
        self.positions = [ wx.Choice(self, wx.ID_ANY, size=(50, -1))
                           for i in range(10) ]
        

        for i in range(10):
            if i < 9:
                gridSizer.Add(wx.StaticText(self, wx.ID_STATIC, "%d" % (i+1)),
                              0, wx.ALL | wx.ALIGN_CENTER, 5)
            else:
                self.pitcherText = wx.StaticText(self, wx.ID_STATIC, "P")
                gridSizer.Add(self.pitcherText,
                              0, wx.ALL | wx.ALIGN_CENTER, 5)
                
            self.players[i].SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            gridSizer.Add(self.players[i], 0, wx.ALL | wx.ALIGN_CENTER, 5)
            wx.EVT_CHOICE(self, self.players[i].GetId(), self.OnSetEntry)
            self.positions[i].SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            gridSizer.Add(self.positions[i], 0, wx.ALL | wx.ALIGN_CENTER, 5)
            wx.EVT_CHOICE(self, self.positions[i].GetId(), self.OnSetEntry)
        sizer.Add(gridSizer, 0, wx.ALL, 0)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"),
                        0, wx.ALL | wx.ALIGN_CENTER, 5)
        buttonSizer.Add(wx.Button(self, wx.ID_OK, "OK"),
                        0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.FindWindowById(wx.ID_OK).Enable(False)
        sizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        self.SetSizer(sizer)
        self.Layout()
        sizer.SetSizeHints(self)

        self.players[-1].Enable(False)
        self.positions[-1].Show(False)

        wx.EVT_BUTTON(self, wx.ID_OK, self.OnOK)

    def OnOK(self, event):
        # Do some validation
        #for row in range(0, 9):
        #    if (self.lineup.GetCellValue(row, 0) == "" or
        #        self.lineup.GetCellValue(row, 1) == ""):
        #        # Eats the event
        #        return

        event.Skip()

    def OnSetEntry(self, event):
        self.CheckValidity()

    def CheckValidity(self):
        """
        Check the status of the lineup after an entry (either a player or his
        position) is set.  Activate the OK button iff the lineup is valid.
        """
        self.pitcherText.Enable(self.HasDH())
        self.players[-1].Enable(self.HasDH())
        self.Layout()

        lineupOK = True

        for slot in range(9):
            if (self.players[slot].GetSelection() == 0 or
                self.positions[slot].GetSelection() == 0):
                lineupOK = False
                break

            if self.HasDH() and self.positions[slot] == 1:
                lineupOK = False
                break

        if self.HasDH():
            numSlots = 10
            if self.players[-1].GetSelection() == 0:
                lineupOK = False
        else:
            numSlots = 9
            
        for slot in range(numSlots):
            for slot2 in range(slot+1, numSlots):
                if (self.players[slot].GetSelection() == 
                    self.players[slot2].GetSelection() or
                    self.positions[slot].GetSelection() ==
                    self.positions[slot2].GetSelection()):
                    lineupOK = False
        
        self.FindWindowById(wx.ID_OK).Enable(lineupOK)

    def LoadRoster(self, roster, team, useDH):
        self.roster = roster
        posList = [ "p", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf" ]
        if useDH:  posList += [ "dh" ]

        fgColors = [ wx.RED, wx.BLUE ]

        for ctrl in self.players:
            ctrl.Clear()
            ctrl.Append("")
            for player in self.roster.Players():
                ctrl.Append(player.GetName())
            ctrl.SetForegroundColour(fgColors[team])
            ctrl.SetSelection(0)

        for ctrl in self.positions:
            ctrl.Clear()
            ctrl.Append("-")
            for pos in posList:  ctrl.Append(pos)
            ctrl.SetForegroundColour(fgColors[team])
            ctrl.SetSelection(0)

    def LoadLineup(self, doc, team):
        gameiter = doc.GetState()
        self.origPlayers = []
        self.origPositions = []

        pitcher = gameiter.GetPlayer(team, 0)
        if pitcher != None:
            self.players[-1].Enable(True)

            for player in self.roster.Players():
                if player.player_id == pitcher:
                    self.players[-1].SetStringSelection(player.GetName())

        for slot in range(9):
            playerId = gameiter.GetPlayer(team, slot+1)
            for player in self.roster.Players():
                if player.player_id == playerId:
                    self.players[slot].SetStringSelection(player.GetName())
                    self.origPlayers.append(self.players[slot].GetSelection())
            if gameiter.GetPosition(team, playerId) <= 10:
                self.positions[slot].SetSelection(gameiter.GetPosition(team, playerId))
            self.origPositions.append(gameiter.GetPosition(team, playerId))
            
        if pitcher != None:
            self.origPlayers.append(self.players[-1].GetSelection())

    def GetPlayerInSlot(self, slot):
        return [x for x in self.roster.Players()][self.players[slot-1].GetSelection()-1]

    def SetPlayerInSlot(self, slot, name, pos):
        if slot > 0:
            self.players[slot-1].SetStringSelection(name)
            self.positions[slot-1].SetSelection(pos)
        else:
            self.players[-1].SetStringSelection(name)
        self.CheckValidity()

    def GetPositionInSlot(self, slot):
        return self.positions[slot-1].GetSelection()

    def HasDH(self):
        for slot in range(9):
            if self.positions[slot].GetSelection() == 10:
                return True
        return False

    def WriteChanges(self, doc, team):
        for slot in range(9):
            if ((self.players[slot].GetSelection() !=
                 self.origPlayers[slot]) or
                (self.positions[slot].GetSelection() !=
                 self.origPositions[slot])):
                player = self.GetPlayerInSlot(slot+1)
                doc.AddSubstitute(player, team, slot+1,
                                  self.positions[slot].GetSelection())

        if self.HasDH():
            if self.players[-1].GetSelection() != self.origPlayers[-1]:
                player = self.GetPlayerInSlot(10)
                doc.AddSubstitute(player, team, 0, 1)

class PinchDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.player = wx.Choice(self, -1, wx.DefaultPosition,
                               wx.Size(300, -1))
        self.player.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        sizer.Add(self.player, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"),
                                 0, wx.ALL | wx.ALIGN_CENTER, 5)
        buttonSizer.Add(wx.Button(self, wx.ID_OK, "OK"), 0,
                        wx.ALL | wx.ALIGN_CENTER, 5)
        self.FindWindowById(wx.ID_OK).Enable(False)
        sizer.Add(buttonSizer, 0, wx.ALIGN_RIGHT, 5)
        
        self.SetSizer(sizer)
        self.Layout()
        sizer.SetSizeHints(self)
        
        wx.EVT_CHOICE(self, self.player.GetId(), self.OnSetPlayer)

    def OnSetPlayer(self, event):
        if self.player.GetSelection() >= 0:
            self.FindWindowById(wx.ID_OK).Enable(True)
            
    def LoadRoster(self, roster, team):
        self.roster = roster

        self.player.Clear()
        for player in self.roster.Players():
            self.player.Append(player.GetName())

        if team == 0:
            self.player.SetForegroundColour(wx.RED)
        else:
            self.player.SetForegroundColour(wx.BLUE)
        
    def WriteChanges(self, doc, oldPlayer, team, pos):
        player = self.GetPlayer()
        gameiter = doc.gameiter
        slot = gameiter.GetSlot(team, oldPlayer)
        doc.AddSubstitute(player, team, slot, pos)

    def GetPlayer(self):
        return [x for x in self.roster.Players()][self.player.GetSelection()]

