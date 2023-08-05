/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 20 Sep 2012 14:46:35 CEST
 *
 * @brief Boost.Python extension to flandmark
 */

#include <boost/python.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/shared_array.hpp>
#include <bob/core/python/gil.h>
#include <bob/core/python/ndarray.h>
#include <cv.h>

#include "flandmark_detector.h"

using namespace boost::python;

static void delete_cascade(CvHaarClassifierCascade* o) {
  cvReleaseHaarClassifierCascade(&o);
}

static void delete_flandmark(FLANDMARK_Model* o) {
  flandmark_free(o);
}

static void delete_image(IplImage* i) {
  i->imageData = 0; ///< never delete blitz::Array data
  cvReleaseImage(&i);
}

static void delete_storage(CvMemStorage* s) {
  cvClearMemStorage(s);
  cvReleaseMemStorage(&s);
}

/**
 * A simple wrapper to operate the flandmark library quickly in iterative
 * environments like Python.
 */
class Localizer {

  public: //api

    /**
     * Constructor, has to load a boosted cascaded from OpenCV and the
     * flandmark model.
     */
    Localizer(const std::string& opencv_cascade,
        const std::string& flandmark_model) : 
      m_cascade((CvHaarClassifierCascade*)cvLoad(opencv_cascade.c_str(), 0, 0, 0), std::ptr_fun(delete_cascade)),
      m_flandmark(flandmark_init(flandmark_model.c_str()), std::ptr_fun(delete_flandmark)),
      m_storage(cvCreateMemStorage(0), std::ptr_fun(delete_storage))
    {
      if( !m_cascade ) {
        PYTHON_ERROR(RuntimeError, "Couldnt load Face detector '%s'", opencv_cascade.c_str());
      }
    
      if ( !m_flandmark ) {
        PYTHON_ERROR(RuntimeError, "Structure model wasn't created. Corrupted file '%s'", flandmark_model.c_str());
      }

      m_landmarks.reset(new float[2*m_flandmark->data.options.M]);
    }

    /**
     * Locates the landmarks from an input image
     */
    tuple operator() (bob::python::const_ndarray input) {
      //checks type
      const bob::core::array::typeinfo& type = input.type();
      if ((type.dtype != bob::core::array::t_uint8) || (type.nd != 2)) {
        PYTHON_ERROR(TypeError, "Input data must be a 2D numpy.array with dtype=uint8 (i.e. a gray-scaled image), but you passed %s", type.str().c_str());
      }

      //converts to IplImage
      boost::shared_ptr<IplImage> ipl_image(cvCreateImageHeader(cvSize(type.shape[1], type.shape[0]), IPL_DEPTH_8U, 1), std::ptr_fun(delete_image));
      ipl_image->imageData = (char*)input.bz<uint8_t,2>().data();

      // Flags for OpenCV face detection
      CvSize minFeatureSize = cvSize(40, 40);
      int flags =  CV_HAAR_DO_CANNY_PRUNING;
      float search_scale_factor = 1.1f;

      // Detect all the faces in the greyscale image.
      CvSeq* rects = cvHaarDetectObjects(ipl_image.get(), m_cascade.get(),
            m_storage.get(), search_scale_factor, 2, flags, minFeatureSize);
      int nFaces = rects->total;

      list retval;
      for (int iface = 0; iface < (rects ? nFaces : 0); ++iface) {

        CvRect* r = (CvRect*)cvGetSeqElem(rects, iface);
        
        dict det;
        det["bbox"] = make_tuple(r->x, r->y, r->width, r->height);
        int bbox[4] = {r->x, r->y, r->x + r->width, r->y + r->height};

        {
          bob::python::no_gil unlock;
          flandmark_detect(ipl_image.get(), bbox, m_flandmark.get(),
              m_landmarks.get());
        }

        list lmlist; ///< landmark list

        // The first point represents the center of the bounding box used by
        // the flandmark library.
        for (int i = 0; i < (2*m_flandmark->data.options.M); i += 2) {
          lmlist.append(make_tuple(m_landmarks[i], m_landmarks[i+1]));
        }
        det["landmark"] = tuple(lmlist);

        retval.append(det);
      }

      return tuple(retval);

    }

  private: //representation

    boost::shared_ptr<CvHaarClassifierCascade> m_cascade;
    boost::shared_ptr<FLANDMARK_Model> m_flandmark;
    boost::shared_ptr<CvMemStorage> m_storage;
    boost::shared_array<float> m_landmarks;

};

BOOST_PYTHON_MODULE(_flandmark) {
  bob::python::setup_python("bindings to flandmark - a library for the localization of facial landmarks");

  class_<Localizer>("Localizer", "A key-point localization for faces using flandmark", init<const std::string&, const std::string&>((arg("detector"), arg("localizer")), "Initializes with both an OpenCV face detector model and an flandmark model"))
    .def("__call__", &Localizer::operator(), (arg("self"), arg("image")), "Locates (possibly multiple) key-points on the given input image. Returns a list of located faces (by OpenCV's model), each attached to a list of key-points.")
    ;
}
