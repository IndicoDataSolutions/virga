#!/bin/bash

uvicorn review_list_page.app:app --host 0.0.0.0 --port 80 --reload