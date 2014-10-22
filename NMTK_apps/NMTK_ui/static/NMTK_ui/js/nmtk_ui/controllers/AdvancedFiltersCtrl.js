/**
 * @license Non-Motorized Toolkit
 * Copyright (c) 2014 Open Technology Group Inc. (A North Carolina Corporation)
 * Developed under Federal Highway Administration (FHWA) Contracts:
 * DTFH61-12-P-00147 and DTFH61-14-P-00108
 * 
 * Redistribution and use in source and binary forms, with or without modification, 
 * are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright notice, 
 *       this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright 
 *       notice, this list of conditions and the following disclaimer 
 *       in the documentation and/or other materials provided with the distribution.
 *     * Neither the name of the Open Technology Group, the name of the 
 *       Federal Highway Administration (FHWA), nor the names of any 
 *       other contributors may be used to endorse or promote products 
 *       derived from this software without specific prior written permission.
 *       
 *       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
 *       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
 *       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
 *       FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
 *       Open Technology Group Inc BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 *       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
 *       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF 
 *       USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED 
 *       AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
 *       OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
 *       OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
 *       SUCH DAMAGE.
 */
define(['underscore'], function (_) {	
	"use strict";
	var controller=['$scope', '$filter', '$log', '$modalInstance', 'filters', 'datafile_api',
        function ($scope, $filter, $log, $modalInstance, filters, datafile_api) {
			/*
			 * Here we are trying to build and apply advanced filters.  This is
			 * tricky mainly because the fields, etc, vary from data file to data
			 * file.
			 */
		    if (_.isUndefined(filters)) {
		    	filters=[];
		    }
			$scope.filters=filters;
			$scope.selected={};
			// A list of all the fields that are available for filtering.
			$scope.selection_fields=JSON.parse(datafile_api.fields);
			$scope.criterion=[  {name: 'Contains (case insensitive)',
				                 filter: 'icontains'}
				              , {name: 'Less than',
		            	  	     filter: 'lt'}
			                  , {name: 'Less than or equal to (<=)',
				                 filter: 'lte'}
			                  , {name: 'Greater than (>)',
				                 filter: 'gt'}
				              , {name: 'Greater than or equal to (>=)',
				                 filter: 'gte'}
			                  , {name: 'Equals (=)',
				                 filter: 'iexact'}
				              , {name: 'Case-insensitive regular expression',
				                 filter: 'iregex'}
				               ]
			$scope.addFilter=function () {
				/*
				 * Add a new filter based on the current contents of 
				 * the $scope.selected object
				 */
				$scope.filters.push($scope.selected);
				$scope.selected={};
			}
			
			$scope.removeFilter=function (input_filter) {
				/*
				 * Iterate over each filter and remove the matched one.
				 */
				
				var pos=null;
				_.find($scope.filters, function (filter, this_pos) {
					if (_.isEqual(filter, input_filter)) {
						pos=this_pos;
						return true
					}
				});
				if (!_.isNull(pos)) {
					$scope.filters.pop(pos);
				}
			}
			
			$scope.gridOptions= {
					 data: 'filters',
					 showFooter: false,
					 showFilter: false,
					 headerRowHeight: 0,
					 enableColumnResize: true,
					 enableRowSelection: false,
					 multiSelect: false,
					 plugins: [new ngGridFlexibleHeightPlugin()],
					 columnDefs: [  { field: 'field',
						              width: 150,
						              displayName: 'Field'}
						          , { field: 'criteria',
						              cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><span ng-cell-text>{{lookupName(row.entity.criteria)}}</span></div>',
						              width: 200,
						              displayName: 'Criteria'}
						          , { field: 'filter_value',
						        	  width: 150,
						        	  displayName: 'Value'}
						          , { displayName: 'Actions',
						              cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><span ng-cell-text><button stop-event="click" class="btn btn-xs btn-danger pull-right" ng-click="removeFilter(row.entity)"><i class="glyphicon glyphicon-remove"></i></button></span></div>'}
						          ],
					 showColumnMenu: false };
			
			
			$scope.lookupName=function (filter) {
				var v=_.find($scope.criterion, function (data) {
					return (data.filter == filter);
				});
				return v.name;
			}
			/*
			 * Our filters always consist of a field name, then a double underscore
			 * and then a filter type.  Here we take the name and split it on the 
			 * __ - then we use addFilterField to add a new field to the list
			 * of filterable fields (So that the on-screen list of filters can
			 * reflect what we have in the existing set of filters.)
			 */
			
			$scope.save=function () {
				$modalInstance.close($scope.filters);
			}
			$scope.close=function() {
				$modalInstance.dismiss();
			}
			

		}			
	];
	return controller;
});