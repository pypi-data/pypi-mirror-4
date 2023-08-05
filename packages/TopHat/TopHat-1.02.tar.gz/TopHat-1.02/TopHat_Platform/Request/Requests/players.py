from Request.request import Request
from Request.requesterrors import NotFound, ServerError, Unauthorised, BadRequest
from Networking.statuscodes import StatusCodes as CODE

from Model.Mapper.gamemapper import GameMapper
from Model.Mapper.playermapper import PlayerMapper
from Model.player import Player
import MySQLdb as mdb

# Decorator
from Model.authentication import require_login, require_super_user

class Players(Request):

	''' 
		API Documentation
		Documentation for the Core Request of Games is available from the TopHat wiki at:
		http://wiki.tophat.ie/index.php?title=Core_Requests:_Players
	'''

	def __init__(self):
		super(Players, self).__init__()

	@require_super_user
	@require_login
	def _doGet(self):
		try:
			
			PM = PlayerMapper()
			
			if self.arg is not None:
				if self.arg.isdigit():
					# Get the user by ID
					player = PM.find(self.arg)
				else:
					raise BadRequest("Players must be requested by ID")

				if player is not None:
					return self._response(player.dict(), CODE.OK)
				else:
					raise NotFound("This player does not exist")
			
			else:

				offset = 0
				players = PM.findAll(offset, offset+50)

				if players is None:
					raise NotFound("There are no players on this system.")

				playerslist = []

				for player in players:
					playerslist.append(player.dict())

				playerslist = {"players":playerslist, "pagination_offset":offset, "max_perpage": 50}

				return self._response(playerslist, CODE.OK)

		except mdb.DatabaseError, e:
				raise ServerError("Unable to search the player database (%s: %s)" % e.args[0], e.args[1])

	@require_login
	def _doPost(self, dataObject):

		if "name" and "game" and "photo" in dataObject:
			try:
				GM = GameMapper()

				if dataObject["game"] is not None and str(dataObject["game"]).isdigit():
					# Get the user by ID
					game = GM.find(str(dataObject["game"]))

					if game is None:
						raise NotFound("The specified player type does not exist.")
				else:
					raise BadRequest("Argument provided for this player type is invalid.")

				print "GAME GOOD "+str(game)
				PM = PlayerMapper()

				player = Player()

				player.setName(dataObject["name"])
				player.setGame(game)
				player.setPhoto(dataObject["photo"])
				player.setUser(self.user)

				PM.insert(player)
				print "PLAYER GOOD "+str(player)

				return self._response(player.dict(3), CODE.CREATED)
				
			except mdb.DatabaseError, e:
				raise ServerError("Unable to search the user database (%s)" % e.args[1])
		else:
			raise BadRequest("Required params name, game and photo not sent")

	@require_login
	def _doPut(self, dataObject):

		if  "id" and ("name" or "photo") in dataObject:
			try:

				PM = PlayerMapper()

				if dataObject["id"] is not None and dataObject["id"].isdigit():
					# Get the user by ID
					player = PM.find(dataObject["id"])

					if player is None:
						raise NotFound("The specified player type does not exist.")
				else:
					raise BadRequest("Argument provided for this player type is invalid.")

				if player.getUser() is self.user or self.user.accessLevel('super_user'):
					if "name" in dataObject:
						player.setName(dataObject["name"])

					if "photo" in dataObject:
						player.setPhoto(dataObject["photo"])

					PM.update(player)

				return self._response(player.dict(3), CODE.CREATED)
				
			except mdb.DatabaseError, e:
				raise ServerError("Unable to search the user database (%s)" % e.args[1])
		else:
			raise BadRequest("Required params name, game and photo not sent")

	@require_login
	def _doDelete(self):
		if self.arg is None:
			raise BadRequest("You must provide the ID of the player to be deleted")
		
		PM = PlayerMapper()

		# get the user if it exists
		try:
			if self.arg.isdigit():
				# Get the user by ID
				player = PM.find(self.arg)
			else:
				raise BadRequest("Players must be requested by ID")

		except mdb.DatabaseError, e:
			raise ServerError("Unable to search the user database (%s: %s)" % e.args[0], e.args[1])

		if player is None:
				raise NotFound("There is no player identified by the number %s" % self.arg)

		# check user has the priviledges
		if not self.user.getId() == player.getUser().getId() and not self.user.accessLevel('super_user'):
			raise Unauthorised("You do not have sufficient privileges to delete this player.")

		# delete the user from the data base
		result = PM.delete(player)

		if result:
			return self._response({"message": "Player Deleted Successfully."}, CODE.OK)
		else:
			raise ServerError("Unable to delete the player")