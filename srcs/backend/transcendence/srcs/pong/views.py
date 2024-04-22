from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging
import json
import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)

def get_canvas(request):
	logger.debug('In get_canvas()')
	if request.method == 'GET':
		logger.debug('about to render!')
		return render(request, "pong/pong.html", {})
		

