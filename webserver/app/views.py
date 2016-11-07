import os
import sys
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, stream_with_context, Response, jsonify
from app import app

import pdb

import time
import json


@app.route('/')
def home():
    title = "VSS"
    listOfImageNames=os.listdir('./app/static/uploads')
    return render_template('home.html', title=title, listOfImageNames=listOfImageNames)


@app.route('/about')
def about():
    title="VSS"
    return render_template('about.html', title=title)
