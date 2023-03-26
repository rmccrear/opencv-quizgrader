import cv2 as cv

def area_of_bounding_rect(r):
    return r[3]*r[2]

def within_percentage(n, m, per):
    e = n*per
    return abs(n-m)<e

def diffence_between_cont_and_bounding_rect_is_within_percentage(cont, per):
    c = cont
    c_area = cv.contourArea(c)
    br = cv.boundingRect(c)
    br_area = area_of_bounding_rect(br)
    #return (within_percentage(br_area, c_area, per), br_area, abs(br_area-c_area))
    return within_percentage(br_area, c_area, per)

def contour_is_rectangular(cont):
    tolerance = .1 # a 10% difference between shape and bounding rect means is is rectangular
    return diffence_between_cont_and_bounding_rect_is_within_percentage(cont, tolerance)

def filter_out_non_rectangles(conts):
    return [cont for cont in conts if contour_is_rectangular(cont)]

def bounding_rectangles_for_contours(conts):
    return [cv.boundingRect(c) for c in conts]

def bounding_rectangles_for_rectangular_shapes(conts):
    return bounding_rectangles_for_contours(filter_out_non_rectangles(conts))
