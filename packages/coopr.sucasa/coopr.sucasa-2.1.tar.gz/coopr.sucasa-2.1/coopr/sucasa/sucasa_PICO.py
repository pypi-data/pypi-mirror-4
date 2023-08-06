#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# This file defines the PICO-specific classes that are customized.
#
# NOTE: we _could_ maintain these files separately, but it's mucn more
# convenient to use them a strings within the SUCASA source.  If this becomes
# a maintenance issue, then we can revisit this decision.
#

from string import Template
import os


sucasa_header=Template("""
//
// ${sucasah}
//
// A template for a user-defined MILP-based application that will be flushed
// out using variables defined by the user.
//
// Note: this file is dynamically created by the sucasa tool.
//
#ifndef ${sucasah_label}
#define ${sucasah_label}

#define PROTECTED_APPINFO ${protected_appinfo}

#include <pico/milpNode.h>
#include <pico/lpSetupObj.h>
#include <pico/BasisArray.h>
#include <pico/BCMip.h>
#include <pico/parBCMip.h>
#include "${app_label}_info.h"

using namespace std;

namespace sucasa_${app_label} {

namespace derived {

//GLOBAL_PARAMETER(debug);

using utilib::IntVector;
using utilib::DoubleVector;
using pebbl::branchSub;
using pebbl::branching;
using pico::PicoLPSolver;
using pico::PicoLPInterface;
using pico::lpSetupObj;
using pico::BasisArray;
using pico::BCMipProblem;

//
// Problem defines an extended MILPProblem, which can incorporate
// application-specific information (e.g. the variable-mapping information)
//
class Problem: virtual public pico::BCMipProblem
#if PROTECTED_APPINFO
                                , public MILPSymbInfo
#else
                                , public MILPSymbFunctions
#endif
{
public:

  /// An empty MILP, for parallel instantiation
  Problem()
#if !PROTECTED_APPINFO
                : MILPSymbFunctions(&app_info)
#endif
  {
  }


  MILPProblem* newMILPProblem()
  {
        return (MILPProblem *) new Problem();
  }

  ///
  virtual ~Problem() {}

  ///
  void init_varmap();

  ///
  void print_summary(ostream& os);

  ///
  Info app_info;
};

//
// MILP defines a serial branch-and-bound algorithm that is derived
// from the MILP branch-and-bound code for mixed-integer linear programming.
//
class MILP: virtual public pico::BCMip
#if PROTECTED_APPINFO
                                , public MILPSymbInfo
#else
                                , public MILPSymbFunctions
#endif
{
protected:

  ///
  friend class MILPNode;

public:

  ///
  MILP() {};

  ///
  virtual ~MILP() {};

  ///
  bool setup(int& argc, char**& argv, Problem& problem_)
        {
        AppMIP = &problem_;
        infoptr = &(problem_.app_info);
        //pico::BCMip::MIP = &problem_;
        bool result =  pico::BCMip::setup(argc,argv, (BCMipProblem&)problem_);
        if (strcmp("${app_label}.row","") != 0)
           problem_.set_labels("${app_label}.row","${app_label}.col");
        problem_.init_varmap();
        //if (debug > 10)
        //   problem_.test_varmap();
        return result;
        }

  /// The application problem.
  Problem *AppMIP;

  ///
  pico::PicoLPInterface* LP()
                {return AppMIP->lp();};

  ///
  branchSub* blankSub();

};


#if defined(ACRO_HAVE_MPI)

///
/// parMILP
///
class parMILP : virtual public pico::parBCMip, virtual public MILP
{
public:

  /// An empty constructor for a branching object
  parMILP()
        {}

  /// A destructor
  virtual ~parMILP()
        {}

  ///
  void reset(bool VBflag=true)
        {
        MILP::reset(VBflag);
        pebbl::parallelBranching::reset(false);
        }

  ///
  pebbl::parallelBranchSub* blankParallelSub();

  /// Pack the branching information into a buffer
  void pack(utilib::PackBuffer& outBuffer)
        {
#if PROTECTED_APPINFO
        MILPSymbInfo::write(outBuffer);
#else
        infoptr->write(outBuffer);
#endif
        pico::parMILP::pack(outBuffer);
        }

  /// Unpack the branching information from a buffer
  void unpack(utilib::UnPackBuffer& inBuffer)
        {
#if PROTECTED_APPINFO
        MILPSymbInfo::read(inBuffer);
#else
        infoptr->read(inBuffer);
#endif
        pico::parMILP::unpack(inBuffer);
        }

  /// Compute the size of the buffer needed for a subproblem
  int spPackSize()
        {
        utilib::PackBuffer pack;
#if PROTECTED_APPINFO
        MILPSymbInfo::write(pack);
#else
        infoptr->write(pack);
#endif
        return pack.size();
        }

  void                 preprocess()
                { pico::parBCMip::preprocess();                        }
  branchSub*        blankSub()
                { return pico::parBCMip::blankSub();                 }
  void                MILPInit(bool initVB=true)
                { pico::parBCMip::MILPInit(initVB);                }
  void                 printAllStatistics(ostream& os = std::cout)
                { pico::parBCMip::printAllStatistics(os);        }
  bool                 setup(int& argc, char**& argv, Problem& p)
        { pico::parBCMip::setup(argc,argv,p); }

};
#endif

//
// MILPNode
//
class MILPNode: virtual public pico::BCMipNode
#if PROTECTED_APPINFO
                                , public MILPSymbInfo
#else
                                , public MILPSymbFunctions
#endif
{
public:

  ///
  MILPNode() {}

  /// Make a root node
  void MILPNodeFromMILP(MILP* master, bool initVB = true);

  /// Make a child node
  void MILPNodeAsChildOf(MILPNode* parent, bool initVB = true);

  /// Dummy destructor
  virtual ~MILPNode() {}

  /// Pointer to the global branching object
  MILP *globalPtr;

  ///
  branching* bGlobal() const
                {return globalPtr;};

  ///
  MILP *global()
                {return globalPtr;};

  /// This functionality is handy at the derived MILPNode level,
  /// but isn't used in the regular MILPNode (yet).
  /// Sets the node (local) bounds on integer variables from
  /// an LP variable number rather than an integer variable number
  void setIntLowerBound(int lpVarNum, int newVal)
        {intLowerBounds[mip()->LPtoIntegerVar[lpVarNum]] = newVal;}

  void setIntUpperBound(int lpVarNum, int newVal)
        {intUpperBounds[mip()->LPtoIntegerVar[lpVarNum]] = newVal;}

};

#if defined(ACRO_HAVE_MPI)
///
/// parMILPNode
///
class parMILPNode : virtual public pico::parBCMipNode, virtual public MILPNode
{
public:

  ///
  pico::branching* bGlobal() const
        {return globalPtr;}

  /// Return a pointer to the global branching object
  parMILP* global() const
        { return globalPtr; }

  /// Return a pointer to the base class of the global branching object
  pebbl::parallelBranching* pGlobal() const
        { return globalPtr; }

  /// An empty constructor for a subproblem
  parMILPNode()
        { }

  /// A virtual destructor for a subproblem
  virtual ~parMILPNode()
        { }

  /**
   * Initialize a subproblem using a branching object
   * This method is not strictly necessary, but its use here illustrates
   * a flexible mechanism for managing the initialization of subproblems.
   * The following crude fragment illustrates some common steps needed in
   * this method.
   */
  void initialize(parMILP* master)
        {
        globalPtr = master;
        MILPNodeFromMILP( (MILP*)master );
        pico::parMILPNode::parMILPNodeFromParMILP(master,false);
        infoptr = globalPtr->infoptr;
        }

 /**
   * Initialize a subproblem as a child of a parent subproblem.
   * This method is not strictly necessary, but its use here illustrates
   * a flexible mechanism for managing the initialization of subproblems.
   * The following crude fragment illustrates some common steps needed in
   * this method.
   */
  void initialize(parMILPNode* parent)
        {
        globalPtr = parent->globalPtr;
        pico::parMILPNode::parMILPNodeAsChildOf(parent);
        infoptr = globalPtr->infoptr;
        }


  /// Pack the information in this subproblem into a buffer
  void pack(utilib::PackBuffer& outBuffer)
        {pico::parMILPNode::pack(outBuffer);}

  /// Unpack the information for this subproblem from a buffer
  void unpack(utilib::UnPackBuffer& inBuffer)
        {pico::parMILPNode::unpack(inBuffer);}

  /// Create a child subproblem of the current subproblem
  virtual parallelBranchSub* makeParallelChild(int whichChild)
        {
        parMILPNode *temp = new parMILPNode;
        temp->initialize(this);
        pico::MILPNode::childInit(temp, whichChild);
        return temp;
        }

  /// void rampUpIncumbentHeuristic(); // called during ramp-up
  /// void quickIncumbentHeuristic();  // called during parallel phase
  branchSub* makeChild(int whichChild = anyChild);

  PicoLPInterface::problemState boundComputationGuts()
                      { return pico::parBCMipNode::boundComputationGuts();}
  lpSetupObj*  makeLPSetupObj()
                      { return pico::parBCMipNode::makeLPSetupObj();  }
  bool         isWarmStart()
                      { return pico::parBCMipNode::isWarmStart();     }
  void         getBasis(BasisArray& basisBuffer)
                      { pico::parBCMipNode::getBasis(basisBuffer); }
  bool               candidateSolution()
                      { return pico::parBCMipNode::candidateSolution();}
  void         getSolution()
                      { pico::parBCMipNode::getSolution();      }
  void         makeActiveLP()
                      { pico::parBCMipNode::makeActiveLP();     }
  int          initialBasisSize()
                      { return pico::parBCMipNode::initialBasisSize(); }
  PicoLPInterface::problemState boundingSolve()
                      { return pico::parBCMipNode::boundingSolve();}
  void         postPseudoCostInit(IntVector&initVars,
                                bool dontRemoveAllBranchChoices,
                                int& numBranches)
                      { pico::parBCMipNode::postPseudoCostInit(
                                              initVars,
                                              dontRemoveAllBranchChoices,
                                              numBranches);
                      }
  void         printMILPNode()
                      { pico::parBCMipNode::printMILPNode();}
  PicoLPInterface::problemState PCInitSolve()
                      { return pico::parBCMipNode::PCInitSolve();}
  void                noLongerActiveLP()
                      { pico::parBCMipNode::noLongerActiveLP();}
  bool                useSavedSolutionNow()
                      { return pico::parBCMipNode::useSavedSolutionNow();}
  void                setBasis()
                      { pico::parBCMipNode::setBasis();}
  void                setBounds()
                      { pico::parBCMipNode::setBounds();}
  void                setupLP(PicoLPInterface *lp)
                      { pico::parBCMipNode::setupLP(lp);}
  bool                updatePCFromBoundingSolve()
                      { return
                        pico::parBCMipNode::updatePCFromBoundingSolve();}

protected:

  /// A pointer to the global branching object
  parMILP* globalPtr;

};
#endif


#if defined(ACRO_HAVE_MPI)
inline pebbl::parallelBranchSub* parMILP::blankParallelSub()
{
  parMILPNode* tmp = new parMILPNode();
  tmp->initialize(this);
  return (pebbl::parallelBranchSub *)tmp;
}
#endif

} // namespace derived

} // namespace sucasa_${app_label}

#endif // ifndef ${sucasah_label}
""")

sucasa_cpp = Template("""
//
// $sucasacpp
//
// Customized branching class for extensions of MILP's
//
// Note: this file is dynamically created by sucasa.
//

#include <strings.h>
#include "${sucasah}"

using namespace utilib;

namespace sucasa_${app_label} {

namespace derived {


branchSub *MILP::blankSub()
{
MILPNode *tmp = new MILPNode;
tmp->MILPNodeFromMILP((MILP *)this);
return (branchSub *) tmp;
}


void MILPNode::MILPNodeFromMILP(MILP *master, bool initVB)
{
globalPtr = master;
infoptr = master->infoptr;
if (initVB)
  pico::BCMipNode::BCMipNodeFromBCMip(master);
}



void MILPNode::MILPNodeAsChildOf(MILPNode* parent, bool initVB)
{
globalPtr = parent->MILPNode::globalPtr;
infoptr = parent->infoptr;
if (initVB)
  pico::BCMipNode::BCMipNodeAsChildOf(parent);
}

void Problem::init_varmap()
{
if (!lp)
   EXCEPTION_MNGR(std::runtime_error, "Problem::init_varmap -- no LP is currently defined!");
BasicArray<CharString> vnames, cnames;
lp()->getVariableNames(vnames);
lp()->getRowNames(cnames);

//
// Initialize symbolic data
//
info().read("${app_label}");
}

/// void MILPNode::incumbentHeuristic() {}

#if defined(ACRO_HAVE_MPI)

branchSub * parMILPNode::makeChild(int whichChild)
{
        return(makeParallelChild(whichChild));
}

/// void parMILPNode::rampUpIncumbentHeuristic()
/// {
///     DEBUGPR(10, ucout << "parMILPNode::rampUpIncumbentHeuristic" <<endl);
///     incumbentHeuristic();
///     pmGlobal()->rampUpIncumbentSync();
/// }
#endif

/// void parMILPNode::rampUpIncumbentHeuristic()
/// {
///     incumbentHeuristic();
/// }


} // namespace derived

} // namespace sucasa_${app_label}
""")


Makefile=Template("""
##
## Makefile generated for the MILP application.
##
## buildFlags.txt is created when configure is run in the top level
## directory.  It contains the build environment macros (CPPFLAGS, etc).

ACRODIR=${acro_dir}
TOPBIN=$$(ACRODIR)/bin
TOPINC=$$(ACRODIR)/include
TOPLIB=$$(ACRODIR)/lib

include $$(ACRODIR)/userapps/buildFlags.txt

## Uncomment to use GLPK
GLPK_LIB= -lOsiGlpk -lglpk

## Uncomment to use SOPLEX
SOPLEX_LIB= -lOsiSpx -lsoplex

## Uncomment to use APPSPACK
## LAPACK_LIBS=/usr/local/lib...
## BLAS_LIBS=/usr/local/lib...
## FLIBS =/usr/local/lib...
## APPSPACKLIB= $$(ACRODIR)/packages/appspack/src/libappspack.a \
##        $$(LAPACK_LIBS) $$(BLAS_LIBS) $$(FLIBS)

## Uncomment to use 3PO
##THREEPOLIB=-l3po

## Uncomment if you need libdl
DLOPEN_LIBS=-ldl

## Uncomment if you need CPLEX
##CPLEX_LIB=/usr/local/lib...
##CPLEX_INCLUDES=-I/

LIBFLAGS=-L$$(TOPLIB) \
        $$(ACRODIR)/packages/pico/src/libpico.a\
        $$(ACRODIR)/packages/pebbl/src/libpebbl.a\
        $$(ACRODIR)/packages/utilib/src/.libs/libutilib.a\
        -lCgl -lOsiClp -lClp $$(SOPLEX_LIB) $$(GLPK_LIB) \
        -lOsi -lCoinUtils $$(CPLEX_LIB) \
         -lamplsolver $$(DLOPEN_LIBS) $$(LIBS) $$(FLIBS) $$(FCLIBS) -llapack -lblas
#
# Paths to:
#  all pico headers, to config.h, and to other configuration headers.
#
INCLUDE_FLAGS=-I. -I$$(TOPINC)/pico -I$$(TOPINC) \
        -I$$(TOPINC)/coin -I$$(TOPINC)/soplex \
        -I$$(TOPINC)/glpk -I$$(TOPINC)/ampl $$(CPLEX_INCLUDES)

OTHER_FLAGS=-DHAVE_CONFIG_H

FLAGS=$$(INCLUDE_FLAGS) $$(OTHER_FLAGS)

all: ${app_label}_milp

${app_label}_milp:        ${app_label}_milp.o ${app_label}_info.o ${app_label}_sucasa.o ${app_label}_extras.o
        $$(CXX) -o PICO_${app_label} ${app_label}_milp.o ${app_label}_info.o ${app_label}_sucasa.o ${app_label}_extras.o $$(LIBFLAGS)


%.o: %.cpp
        $$(CXX) $$(FLAGS) $$(CXXFLAGS) -c -o $$@ $$<

delete:
        - @$$(RM) -f ${app_label}.row ${app_label}.col ${app_label}.val ${app_label}_sucasa.cpp ${app_label}_sucasa.h ${app_label}_info.h ${app_label}_info.cpp ${app_label}.map ${app_label}_sucasa.o ${app_label}_info.o ${app_label}_sucasa.o ${app_label}_extras.o PICO_${app_label} SunWS* *.o ${app_label}.mps ampl_script.in parsetab.py parsetab.pyc ampl.out

clean:
        $$(RM) *.o
""")

header=Template("""
//
// $ofileh
//
// A template for a user-defined MILP-based application that will be flushed
// out using variables defined by the user.
//
// Note: this file is dynamically created by sucasa, but
// once it exists sucasa will not over-write it.
//
#ifndef ${ofileh_label}
#define ${ofileh_label}

#include "${sucasah}"

namespace sucasa_${app_label} {

using pebbl::branchSub;
using pebbl::branching;

//
// Problem defines an extended MILPProblem, which can incorporate
// application-specific information (e.g. the variable-mapping information)
//
class Problem: virtual public derived::Problem
{
public:

  /// An empty MILP, for parallel instantiation
  Problem() {}

  MILPProblem* newMILPProblem()
  { return (MILPProblem *) new Problem(); }

  ///
  virtual ~Problem() {}

  ///
  void print_summary(ostream& os);
};


//
// MILP defines a serial branch-and-bound algorithm that is derived
// from the MILP branch-and-bound code for mixed-integer linear programming.
//
class MILP: virtual public derived::MILP
{
protected:

  ///
  friend class MILPNode;

public:

  ///
  MILP() {}

  ///
  virtual ~MILP() {}

  ///
  branchSub* blankSub();

  ///
  bool haveIncumbentHeuristic() {return false;}

  //void serialPrintSolution(const char* header = "",
                             //const char* footer = "",
                             //ostream& outStream = cout);

  //void newIncumbentEffect(double new_value);

  //void printAllStatistics(std::ostream& stream = std::cout)
  //{};

  /// Update the incumbent from a search leaf
  //void updateIncumbent(DoubleVector& newSolution, double solutionValue);

/// Designate some variables as more important for branching than others.
/// For example, it's best to decide if you'll build a facility at all before
/// you decide its color.

//  void initializeBranchingPriorities();

};


#if defined(ACRO_HAVE_MPI)

///
/// parMILP
///
class parMILP : virtual public derived::parMip, virtual public MILP
{
public:

  /// An empty constructor for a branching object
  parMILP()
        {}

  /// A destructor
  virtual ~parMILP()
        {}

  ///
  void reset(bool VBflag=true)
        {
        MILP::reset(VBflag);
        pebbl::parallelBranching::reset(false);
        }

  /// Hook to read in user-defined parameters
  //void readIn(int argc, char** argv)
        //{}

  ///
  pebbl::parallelBranchSub* blankParallelSub();

  /// Pack the branching information into a buffer
  //void pack(utilib::PackBuffer& outBuffer) {}

  /// Unpack the branching information from a buffer
  //void unpack(utilib::UnPackBuffer& inBuffer) {}

  /// Compute the size of the buffer needed for a subproblem
  //int spPackSize() {}

  //void                 preprocess()
                //{ pico::parBCMip::preprocess();                        }
  //branchSub*        blankSub()
                //{ return pico::parBCMip::blankSub();                 }
  //void                MILPInit(bool initVB=true)
                //{ pico::parBCMip::MILPInit(initVB);                }
  //void                 printAllStatistics(ostream& os = std::cout)
                //{ pico::parBCMip::printAllStatistics(os);        }
  //bool                 setup(int& argc, char**& argv, Problem& p)
        //{ pico::parBCMip::setup(argc,argv,p); }

};
#endif

//
// MILPNode
//
class MILPNode: virtual public derived::MILPNode
{
public:

  ///
  MILPNode() {}

  /// Make a root node
  void MILPNodeFromMILP(MILP* master, bool initVB = true);

  /// Make a child node
  void MILPNodeAsChildOf(MILPNode* parent, bool initVB = true);

  /// Dummy destructor
  virtual ~MILPNode() {}

  /// Pointer to the global branching object
  MILP *globalPtr;

  ///
  branching* bGlobal() const
                {return globalPtr;};

  ///
  MILP *global()
                {return globalPtr;};

  /// This functionality is handy at the derived MILPNode level,
  /// but isn't used in the regular MILPNode (yet).
  /// Sets the node (local) bounds on integer variables from
  /// an LP variable number rather than an integer variable number
  //void setIntLowerBound(int lpVarNum, int newVal)
        //{intLowerBounds[mip()->LPtoIntegerVar[lpVarNum]] = newVal;}

  //void setIntUpperBound(int lpVarNum, int newVal)
        //{intUpperBounds[mip()->LPtoIntegerVar[lpVarNum]] = newVal;}

  /// void incumbentHeuristic();       // your incumbent (quick.. calls this)

  /// pebbl::solution* extractSolution();

  /// void boundComputation(double *);    // your bound computation

  // For pmedian ///////////////////////////////////////////////////////
  // We'll call the MILP-level updateIncumbent when necessary.  The milpNode version
  // is almost entirely LP-based-specific checks, etc.  If we ever enumerate,
  // in a B&B setting, we will have to put enumeration-related material here.
  //
  //void updateIncumbent();
  //////////////////////////////////////////////////////////////////////


};

#if defined(ACRO_HAVE_MPI)
///
/// parMILPNode
///
class parMILPNode : virtual public derived::parMILPNode, virtual public MILPNode
{
public:

  ///
  pico::branching* bGlobal() const
        {return globalPtr;}

  /// Return a pointer to the global branching object
  parMILP* global() const
        { return globalPtr; }

  /// Return a pointer to the base class of the global branching object
  pebbl::parallelBranching* pGlobal() const
        { return globalPtr; }

  /// An empty constructor for a subproblem
  parMILPNode()
        { }

  /// A virtual destructor for a subproblem
  virtual ~parMILPNode()
        { }

  /**
   * Initialize a subproblem using a branching object
   * This method is not strictly necessary, but its use here illustrates
   * a flexible mechanism for managing the initialization of subproblems.
   * The following crude fragment illustrates some common steps needed in
   * this method.
   */
  void initialize(parMILP* master)
        {
        globalPtr = master;
        MILPNodeFromMILP( (MILP*)master );
        pico::parMILPNode::parMILPNodeFromParMILP(master,false);
        infoptr = globalPtr->infoptr;
        }

 /**
   * Initialize a subproblem as a child of a parent subproblem.
   * This method is not strictly necessary, but its use here illustrates
   * a flexible mechanism for managing the initialization of subproblems.
   * The following crude fragment illustrates some common steps needed in
   * this method.
   */
  void initialize(parMILPNode* parent)
        {
        globalPtr = parent->globalPtr;
        pico::parMILPNode::parMILPNodeAsChildOf(parent);
        infoptr = globalPtr->infoptr;
        }


  /// Pack the information in this subproblem into a buffer
  //void pack(utilib::PackBuffer& outBuffer)
        //{pico::parMILPNode::pack(outBuffer);}

  /// Unpack the information for this subproblem from a buffer
  //void unpack(utilib::UnPackBuffer& inBuffer)
        //{pico::parMILPNode::unpack(inBuffer);}

  /// Create a child subproblem of the current subproblem
  virtual parallelBranchSub* makeParallelChild(int whichChild)
        {
        parMILPNode *temp = new parMILPNode;
        temp->initialize(this);
        pico::MILPNode::childInit(temp, whichChild);
        return temp;
        }

  /// void rampUpIncumbentHeuristic(); // called during ramp-up
  /// void quickIncumbentHeuristic();  // called during parallel phase
  branchSub* makeChild(int whichChild = anyChild);

  //PicoLPInterface::problemState boundComputationGuts()
                      //{ return pico::parBCMipNode::boundComputationGuts();}
  //lpSetupObj*  makeLPSetupObj()
                      //{ return pico::parBCMipNode::makeLPSetupObj();  }
  //bool         isWarmStart()
                      //{ return pico::parBCMipNode::isWarmStart();     }
  //void         getBasis(BasisArray& basisBuffer)
                      //{ pico::parBCMipNode::getBasis(basisBuffer); }
  //bool               candidateSolution()
                      //{ return pico::parBCMipNode::candidateSolution();}
  //void         getSolution()
                      //{ pico::parBCMipNode::getSolution();      }
  //void         makeActiveLP()
                      //{ pico::parBCMipNode::makeActiveLP();     }
  //int          initialBasisSize()
                      //{ return pico::parBCMipNode::initialBasisSize(); }
  //PicoLPInterface::problemState boundingSolve()
                      //{ return pico::parBCMipNode::boundingSolve();}
  //void         postPseudoCostInit(IntVector&initVars,
                                //bool dontRemoveAllBranchChoices,
                                //int& numBranches)
                      //{ pico::parBCMipNode::postPseudoCostInit(
                                              //initVars,
                                              //dontRemoveAllBranchChoices,
                                              //numBranches);
                      //}
  //void         printMILPNode()
                      //{ pico::parBCMipNode::printMILPNode();}
  //PicoLPInterface::problemState PCInitSolve()
                      //{ return pico::parBCMipNode::PCInitSolve();}
  //void                noLongerActiveLP()
                      //{ pico::parBCMipNode::noLongerActiveLP();}
  //bool                useSavedSolutionNow()
                      //{ return pico::parBCMipNode::useSavedSolutionNow();}
  //void                setBasis()
                      //{ pico::parBCMipNode::setBasis();}
  //void                setBounds()
                      //{ pico::parBCMipNode::setBounds();}
  //void                setupLP(PicoLPInterface *lp)
                      //{ pico::parBCMipNode::setupLP(lp);}
  //bool                updatePCFromBoundingSolve()
                      //{ return
                        //pico::parBCMipNode::updatePCFromBoundingSolve();}

protected:

  /// A pointer to the global branching object
  parMILP* globalPtr;

};
#endif


#if defined(ACRO_HAVE_MPI)
inline pebbl::parallelBranchSub* parMILP::blankParallelSub()
{
  parMILPNode* tmp = new parMILPNode();
  tmp->initialize(this);
  return (pebbl::parallelBranchSub *)tmp;
}
#endif

} // namespace sucasa_${app_label}

#endif // ifndef ${sucasah_label}
""")

extras=Template("""
//
// Note: this file is automatically generated if the user does not create it.
//

#include "${app_label}_milp.h"

namespace sucasa_${app_label} {

} // namespace sucasa_${app_label}

""")

source=Template("""
//
// Note: this file is dynamically created by sucasa if the user does
// not create it.  Once it it exists sucasa will not over-write it.
//
#include "${app_label}_milp.h"

namespace sucasa_${app_label} {

void Problem::print_summary(ostream& ) {}

branchSub *MILP::blankSub()
{
MILPNode *tmp = new MILPNode;
tmp->MILPNodeFromMILP((MILP *)this);
return (branchSub *) tmp;
}

void MILPNode::MILPNodeFromMILP(MILP *master, bool initVB)
{
globalPtr = master;
infoptr = master->infoptr;
if (initVB)
    derived::MILPNode::MILPNodeFromMILP(master);
}

void MILPNode::MILPNodeAsChildOf(MILPNode* parent, bool initVB)
{
globalPtr = parent->MILPNode::globalPtr;
infoptr = parent->infoptr;
if (initVB)
    derived::MILPNode::MILPNodeAsChildOf(parent);
}


} // namespace sucasa_${app_label}
""")

main=Template("""
int main(int argc, char** argv)
{
try {

  InitializeTiming();
  int nprocessors=1;

#ifdef ACRO_HAVE_MPI

  uMPI::init(&argc,&argv,MPI_COMM_WORLD);
  nprocessors = uMPI::size;

  if (nprocessors > 1) {
     CommonIO::begin();
     CommonIO::setIOFlush(1);

     sucasa_${app_label}::parMILP milp;
     sucasa_${app_label}::Problem problem;
     if (milp.setup(argc,argv,problem)) {
        milp.reset();
        milp.solve();
        }
     CommonIO::end();
     }
#endif

  if (nprocessors == 1) {
     sucasa_${app_label}::MILP milp;
     sucasa_${app_label}::Problem problem;

     if (milp.setup(argc,argv,problem)) {
        milp.reset();
        milp.solve();
        }
     }

#ifdef ACRO_HAVE_MPI
  uMPI::done();
#endif

}
STD_CATCH(;)

return 0;
}
""")


def create_customized_files(app_label="unknown", create_main=True, protected=0, acro_dir="../../"):
    """
    Generate source, header and Makefiles for a customized PICO solver that uses the
    symbolic information generated by SUCASA.
    """
    if protected is False:
        protected=0
    elif protected is True:
        protected=1
    #
    # Define filenames
    #
    sucasah_label=app_label+"_sucasa"
    sucasah=sucasah_label+".h"
    sucasacpp=sucasah_label+".cpp"
    ofileh_label=app_label+"_milp"
    ofileh=ofileh_label+".h"
    ofilecpp=ofileh_label+".cpp"
    ofilecpp_extras=app_label+"_extras.cpp"
    #
    # Construct the SUCASA header
    #
    file = sucasa_header.substitute(app_label=app_label, sucasah=sucasah, sucasah_label=sucasah_label, sucasacpp=sucasacpp, protected_appinfo=protected, acro_dir=acro_dir)
    OUTPUT=open(sucasah,"w")
    OUTPUT.write(file+'\n')
    OUTPUT.close()
    #
    # Construct the SUCASA source
    #
    file = sucasa_cpp.substitute(app_label=app_label, sucasah=sucasah, sucasah_label=sucasah_label, sucasacpp=sucasacpp, protected_appinfo=protected, acro_dir=acro_dir)
    OUTPUT=open(sucasacpp,"w")
    OUTPUT.write(file+'\n')
    OUTPUT.close()
    #
    # Construct the Makefile
    #
    file = Makefile.substitute(app_label=app_label, ofileh=ofileh, ofileh_label=ofileh_label, ofilecpp=ofilecpp, protected_appinfo=protected, acro_dir=acro_dir)
    OUTPUT=open("Makefile","w")
    OUTPUT.write(file+'\n')
    OUTPUT.close()

    files=[sucasah, sucasacpp, "Makefile"]

    if not os.path.exists(ofileh):
        #
        # Construct the header file
        #
        file = header.substitute(app_label=app_label, ofileh=ofileh, ofileh_label=ofileh_label, ofilecpp=ofilecpp, sucasah=sucasah, sucasah_label=sucasah_label, protected_appinfo=protected)
        OUTPUT=open(ofileh,"w")
        OUTPUT.write(file+'\n')
        OUTPUT.close()
        files.append(ofileh)
    if not os.path.exists(ofilecpp):
        #
        # Construct the source file
        #
        file = source.substitute(app_label=app_label, ofileh=ofileh, ofileh_label=ofileh_label, ofilecpp=ofilecpp, protected_appinfo=protected)
        if create_main:
            file += main.substitute(app_label=app_label, ofileh=ofileh, ofileh_label=ofileh_label, ofilecpp=ofilecpp, protected_appinfo=protected)
        OUTPUT=open(ofilecpp,"w")
        OUTPUT.write(file+'\n')
        OUTPUT.close()
        files.append(ofilecpp)
    if not os.path.exists(ofilecpp_extras):
        #
        # Construct the extras file
        #
        file = extras.substitute(app_label=app_label, ofileh=ofileh, ofileh_label=ofileh_label, ofilecpp=ofilecpp, sucasah=sucasah, sucasah_label=sucasah_label, protected_appinfo=protected)
        OUTPUT=open(ofilecpp_extras,"w")
        OUTPUT.write(file+'\n')
        OUTPUT.close()
        files.append(ofilecpp_extras)
    #
    # Return a list of the files created
    #
    return files
