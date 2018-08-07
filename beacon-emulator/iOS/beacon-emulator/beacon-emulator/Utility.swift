//
//  Utility.swift
//  beacon-emulator
//
//  Created by Michael Vartanian on 8/7/18.
//  Copyright © 2018 Michael Vartanian. All rights reserved.
//

import Foundation
import UIKit

// Creating a GradientLayer - Adopted from AppCoda
// https://www.appcoda.com/cagradientlayer/
func createGradientLayer(inputViewController: UIViewController, gradientLayer: CAGradientLayer, startColor: UIColor, endColor: UIColor) {
    //gradientLayer = CAGradientLayer()
    
    gradientLayer.frame = inputViewController.view.bounds
    
    //gradientLayer.colors = [UIColor.darkGray.cgColor, UIColor.lightGray.cgColor]
    gradientLayer.colors = [startColor.cgColor, endColor.cgColor]
    
    
    // Put at index 0 to put in background
    // https://stackoverflow.com/questions/41851067/push-gradient-layer-to-background-swift
    inputViewController.view.layer.insertSublayer(gradientLayer, at: 0)
}

func updateToggleButton(button: UIButton, stateOneColor: UIColor, stateOneText: String, stateTwoColor: UIColor, stateTwoText: String) {
    
    // Update button title/background based on state
    // If campaign is active - green, else red
    if button.isSelected {
        button.setTitle(stateOneText, for: .normal)
        button.backgroundColor = stateOneColor
    }
    else {
        button.setTitle(stateTwoText, for: .normal)
        button.backgroundColor = stateTwoColor
    }
}
